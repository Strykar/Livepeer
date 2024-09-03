import sqlite3
import csv
from config import ISO_CSV_PATH, AIRPORT_CSV_PATH, DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ip_addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT UNIQUE,
        location TEXT,
        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS airport_codes (
        iata_code TEXT PRIMARY KEY,
        latitude REAL,
        longitude REAL
    )
    ''')
    conn.commit()
    return conn

def load_iso_codes():
    iso_codes = {}
    with open(ISO_CSV_PATH, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            iso_codes[row['alpha-2'].upper()] = row
            iso_codes[row['alpha-3'].upper()] = row
    return iso_codes

def load_airport_data(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM airport_codes")  # Clear previous data
    with open(AIRPORT_CSV_PATH, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
            INSERT INTO airport_codes (iata_code, latitude, longitude)
            VALUES (?, ?, ?)
            ''', (row['iata_code'], float(row['latitude']), float(row['longitude'])))
    conn.commit()
