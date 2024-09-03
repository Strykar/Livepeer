import geoip2.database
from config import DB_FILE

# https://git.io/GeoLite2-City.mmdb or https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb
reader = geoip2.database.Reader('/path/to/GeoLite2-City.mmdb')

def get_ip_geolocation(ip):
    try:
        response = reader.city(ip)
        return {
            "country": response.country.name,
            "city": response.city.name,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude
        }
    except geoip2.errors.AddressNotFoundError:
        return None
