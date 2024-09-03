from config import DB_FILE, LPT_DNS
from utils.database import init_db, load_iso_codes, load_airport_data
from utils.geoip import get_ip_geolocation
from utils.networking import resolve_domain, ping_ip
from utils.airports import find_closest_airport
from utils.smokeping import generate_smokeping_config, save_smokeping_config
import argparse
from collections import defaultdict
import os

def main():
    parser = argparse.ArgumentParser(description="Smokeping configuration updater for Livepeer nodes.")
    parser.add_argument('--dry-run', action='store_true', help="Resolve, geolocate, and print the GPU server locations and corresponding Livepeer nodes.")
    parser.add_argument('--print-config', action='store_true', help="Print the Smokeping config that will be used.")
    parser.add_argument('--gpu-locations', type=str, help="Comma-separated list of GPU server locations in the format 'LPT-ISO_COUNTRY_CODE'.")
    parser.add_argument('--gpu-config-file', type=str, help="Path to a flat file containing GPU server locations.")
    parser.add_argument('--lptdns', type=str, default=LPT_DNS, help="Specify the Livepeer DNS name to resolve IPs. Overrides the default in config.py.")
    args = parser.parse_args()

    if not args.gpu_locations and not args.gpu_config_file:
        print("Error: Either --gpu-locations or --gpu-config-file must be provided.")
        return

    if args.gpu_config_file and not os.path.exists(args.gpu_config_file):
        print(f"Error: Config file {args.gpu_config_file} does not exist.")
        return

    # Load GPU locations
    if args.gpu_locations:
        gpu_locations_str = args.gpu_locations
    elif args.gpu_config_file:
        with open(args.gpu_config_file, 'r') as f:
            gpu_locations_str = f.read().strip()

    conn = init_db()
    iso_codes = load_iso_codes()
    load_airport_data(conn)

    try:
        gpu_locations = parse_gpu_locations(gpu_locations_str, iso_codes)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Use the specified domain (from config or CLI)
    domain = args.lptdns
    livepeer_ips = resolve_domain(domain)
    if not livepeer_ips:
        print(f"Failed to resolve IPs for the domain '{domain}'.")
        return

    geolocated_ips = defaultdict(list)
    for ip in livepeer_ips:
        if ping_ip(ip):
            geo_info = get_ip_geolocation(ip)
            if geo_info:
                for location, country in gpu_locations.items():
                    if geo_info['country'] == country:
                        store_ip(conn, ip, location)
                        lat, lon = geo_info['latitude'], geo_info['longitude']
                        closest_airport = find_closest_airport(lat, lon, conn)
                        print(f"{location} -- {geo_info['city']} (Closest Airport: {closest_airport})")
                        geolocated_ips[location].append(ip)

    # Generate the Smokeping configuration
    config_content = generate_smokeping_config(geolocated_ips, gpu_locations)
    
    # Save the configuration (if not in dry-run mode)
    if not args.dry_run:
        save_smokeping_config(config_content)
    else:
        print(config_content)

    conn.close()

if __name__ == "__main__":
    main()
