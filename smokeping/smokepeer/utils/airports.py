from haversine import haversine
import sqlite3

def find_closest_airport(lat, lon, conn):
    closest_airport = None
    min_distance = float('inf')

    cursor = conn.cursor()
    cursor.execute("SELECT iata_code, latitude, longitude FROM airport_codes")
    for row in cursor.fetchall():
        airport_lat, airport_lon = row[1], row[2]
        distance = haversine((lat, lon), (airport_lat, airport_lon))
        if distance < min_distance:
            min_distance = distance
            closest_airport = row[0]  # IATA code

    return closest_airport
