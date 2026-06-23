# SSH Honeypot with Live Dashboard

A fake SSH server that logs every brute-force attempt and displays attacker data in real-time on an interactive world map dashboard. Built for educational purposes as part of my network security studies at ISETCOM.

---

## Dashboard Preview

> World map with live attack markers, credential charts, and attack timeline.

<img width="1917" height="787" alt="dashboard" src="https://github.com/user-attachments/assets/ec0869c4-08d2-4b4e-9b1c-4be3b814f85c" />

<img width="1918" height="780" alt="dashboard1" src="https://github.com/user-attachments/assets/14b14a1e-6af4-4f64-b235-905b0cdd4371" />


---

## How it works

1. The honeypot listens on port 22 pretending to be a real SSH server
2. Attackers connect and try username/password combinations
3. Every attempt is logged — nobody ever gets in
4. Each attacker IP is automatically enriched with:
   - Geolocation (country, city, coordinates)
   - ISP / ASN info
   - Abuse reputation score via AbuseIPDB
5. Everything appears live on the dashboard within seconds

---

## Architecture
Attacker ──→ Fake SSH Server (Paramiko)

│

▼

Threat Intel Enrichment

├── ip-api.com   → geolocation + ISP

└── AbuseIPDB    → reputation score (0-100)

│

▼

SQLite Database

│

▼

Flask Dashboard (polls every 5s)

├── World map        (Leaflet.js)

├── Top usernames     (Chart.js)

├── Top passwords     (Chart.js)

└── Attacks over time (Chart.js)
## Stack

| Layer | Technology |
|---|---|
| Fake SSH server | Python, Paramiko |
| Threat intelligence | ip-api.com, AbuseIPDB |
| Database | SQLite |
| Backend | Python, Flask |
| Frontend | HTML, Chart.js, Leaflet.js |
## Run locally

```bash
# clone the repo
git clone https://github.com/ahmedyassine-loussaief/honeypot.git
cd honeypot

# install dependencies
pip3 install -r requirements.txt --break-system-packages

# terminal 1 — start the honeypot
python3 honeypot.py

# terminal 2 — start the dashboard
python3 dashboard.py
```

Open `http://127.0.0.1:5000` in your browser.

> By default the honeypot listens on port **2222** for local testing.

## Disclaimer

This project is built strictly for educational purposes and cybersecurity research.
Only deploy on systems you own. Never use against networks or machines without explicit permission.

## Author
**Ahmed Yassine Loussaief** 
L2 Sécurité Réseaux — ISETCOM 
[GitHub](https://github.com/ahmedyassine-loussaief)
