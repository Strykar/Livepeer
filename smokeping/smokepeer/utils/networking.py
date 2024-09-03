import socket
import subprocess

def resolve_domain(domain):
    try:
        return socket.gethostbyname_ex(domain)[2]
    except socket.gaierror:
        return []

def ping_ip(ip):
    result = subprocess.run(['ping', '-c', '3', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0
