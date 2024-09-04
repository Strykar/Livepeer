"""
This script tests network connectivity, DNS, and Arbitrum RPC availability
Use with systemd as ExecStartPre=lpt_execstartpre.py
"""

import sys
import time
import socket
import subprocess
import logging
import requests
from systemd.journal import JournalHandler

# User config starts
URL = "https://arb1.arbitrum.io/rpc"
DOMAIN = "arb1.arbitrum.io"
INITIAL_SLEEP_INTERVAL = 5  # Start with 5 seconds for backoff
TIMEOUT = 600       # Max time to wait is 10 minutes
MAX_RETRIES = 21    # Retry up to 21 times (adjustable)
# User-configurable variables for network connectivity check
PING_HOST = "8.8.8.8"  # Default to Google's DNS, but can be any host
PING_COUNT = 1         # Number of pings to send
PING_TIMEOUT = 2       # Timeout for each ping attempt, in seconds
# User config ends

# Set up logging to systemd journal
logger = logging.getLogger('lpt_execstartpre')
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)

def log_message(message, level=logging.DEBUG):
    """Log a message."""
    logger.log(level, message)

def is_connected(host=PING_HOST, count=PING_COUNT, timeout=PING_TIMEOUT):
    """Check for network connectivity by pinging the specified host."""
    log_message(f"Checking network connectivity by pinging {host}...")
    try:
        subprocess.check_call(
            ["ping", "-c", str(count), "-W", str(timeout), host],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def is_dns_resolved(domain):
    """Check if the domain resolves to an IP address."""
    log_message(f"Checking DNS resolution for {domain}...")
    try:
        socket.gethostbyname(domain)
        return True
    except socket.error:
        return False

def rpc_query(url):
    """Send a POST request to the RPC server and check if 'result' is in the response."""
    log_message(f"Sending RPC query to {url}...")
    headers = {"Content-Type": "application/json"}
    data = '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return "result" in response.json()
    except requests.RequestException as e:
        log_message(f"RPC query failed: {e}", logging.ERROR)
        return False

def main():
    """Main function to handle retries and falloff."""
    sleep_interval = INITIAL_SLEEP_INTERVAL  # Local variable
    retry_count = 0
    start_time = time.time()

    while True:
        # Check for network connectivity
        if not is_connected():
            log_message(
                f"No network connectivity. Retrying in {sleep_interval} seconds.",
                logging.WARNING
            )
            time.sleep(sleep_interval)
            continue

        # Check if the domain resolves
        if not is_dns_resolved(DOMAIN):
            log_message(
                f"DNS resolution for {DOMAIN} failed. Retrying in {sleep_interval} seconds.",
                logging.WARNING
            )
            time.sleep(sleep_interval)
            continue

        # Check if the RPC request succeeds
        if rpc_query(URL):
            log_message(f"DNS and RPC query for {DOMAIN} successful.", logging.INFO)
            sys.exit(0)

        retry_count += 1
        elapsed_time = time.time() - start_time

        if elapsed_time >= TIMEOUT or retry_count >= MAX_RETRIES:
            log_message(
                f"Timeout reached: DNS or RPC query for {DOMAIN} failed after "
                f"{int(elapsed_time)} seconds or {retry_count} retries.",
                logging.ERROR
            )
            sys.exit(1)

        log_message(
            f"Attempt {retry_count} failed. Retrying in {sleep_interval} seconds...",
            logging.WARNING
        )
        time.sleep(sleep_interval)

        # Increase sleep time with exponential backoff, but cap at 30 seconds
        sleep_interval = min(sleep_interval * 2, 30)

if __name__ == "__main__":
    sys.exit(main())
