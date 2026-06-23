# database.py - handles all SQLite storage for attack logs
import sqlite3
from datetime import datetime

DB_FILE = "honeypot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip TEXT,
            username TEXT,
            password TEXT,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            isp TEXT,
            abuse_score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_attack(ip, username, password, geo_data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO attacks 
        (timestamp, ip, username, password, country, city, latitude, longitude, isp, abuse_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ip,
        username,
        password,
        geo_data.get("country", "Unknown"),
        geo_data.get("city", "Unknown"),
        geo_data.get("lat", 0),
        geo_data.get("lon", 0),
        geo_data.get("isp", "Unknown"),
        geo_data.get("abuse_score", 0)
    ))
    conn.commit()
    conn.close()

def get_all_attacks():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM attacks ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM attacks").fetchone()[0]
    unique_ips = c.execute("SELECT COUNT(DISTINCT ip) FROM attacks").fetchone()[0]
    top_country = c.execute("""
        SELECT country, COUNT(*) as cnt 
        FROM attacks 
        GROUP BY country 
        ORDER BY cnt DESC 
        LIMIT 1
    """).fetchone()
    conn.close()
    return {
        "total": total,
        "unique_ips": unique_ips,
        "top_country": top_country[0] if top_country else "N/A"
    }
