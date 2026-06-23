# honeypot.py - fake SSH server that logs every attack attempt
import paramiko
import socket
import threading
import logging
import requests
from database import init_db, log_attack


logging.getLogger("paramiko").setLevel(logging.CRITICAL)

HOST = "0.0.0.0"  # listen on all interfaces
PORT = 2222       # use 2222 locally, change to 22 on real server

HOST_KEY = paramiko.RSAKey.generate(2048)

def get_threat_intel(ip):
    # enrich attacker IP with geolocation and abuse data
    geo = {}
    try:
        # ip-api.com gives us location and ISP for free
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = r.json()
        if data.get("status") == "success":
            geo["country"] = data.get("country", "Unknown")
            geo["city"] = data.get("city", "Unknown")
            geo["lat"] = data.get("lat", 0)
            geo["lon"] = data.get("lon", 0)
            geo["isp"] = data.get("isp", "Unknown")
    except:
        geo = {"country": "Unknown", "city": "Unknown",
               "lat": 0, "lon": 0, "isp": "Unknown"}

    try:
        ABUSEIPDB_KEY = "7ca94ae72831ed337dc918d53091d788b427f250e69dc33127c3fb659d9b8e28396feb3b1edecc84"  
        headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        r2 = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers=headers,
            params=params,
            timeout=3
        )
        data2 = r2.json()
        geo["abuse_score"] = data2.get("data", {}).get("abuseConfidenceScore", 0)
    except:
        geo["abuse_score"] = 0

    return geo

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_channel_request(self, kind, chanid):
        # accept channel requests so attacker thinks they're connecting
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # this is where we log every login attempt
        print(f"[!] Attack from {self.client_ip} — "
              f"tried {username}:{password}")
        geo = get_threat_intel(self.client_ip)
        log_attack(self.client_ip, username, password, geo)
        # always deny we just want to log, not let anyone in
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

def handle_connection(client_socket, client_ip):
    # handle one attacker connection
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        server = FakeSSHServer(client_ip)
        transport.start_server(server=server)
        # keep connection open briefly so attacker tries more passwords
        chan = transport.accept(30)
        if chan:
            chan.close()
    except Exception:
        pass
    finally:
        client_socket.close()

def start_honeypot():
    init_db()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(100)
    print(f"[*] Honeypot listening on port {PORT}")
    print(f"[*] Waiting for attackers...\n")

    while True:
        client_socket, addr = server_socket.accept()
        client_ip = addr[0]
        # handle each attacker in its own thread
        t = threading.Thread(
            target=handle_connection,
            args=(client_socket, client_ip)
        )
        t.daemon = True
        t.start()

if __name__ == "__main__":
    start_honeypot()
