import socket

def generate_smokeping_config(livepeer_ips, gpu_locations):
    """
    Generate the Smokeping configuration content based on the provided IP addresses and GPU locations.
    Each target host will include a geolocated label in the graph name.

    :param livepeer_ips: Dictionary mapping locations to lists of IP addresses.
    :param gpu_locations: Dictionary mapping GPU location codes to country names.
    :return: String representing the Smokeping configuration content.
    """
    # Prepend the required header to the configuration
    config_output = """*** General ***

owner     = Avi H.D.                            # your name
contact   = strykar@hotmail.com                       # your email
mailhost  = smtp.gmail.com                      # your mail server
sendmail  = /bin/false                                # where the sendmail program is
imgcache  = /srv/smokeping/imgcache                   # filesystem directory where we store files
imgurl    = imgcache                                  # URL directory to find them
datadir   = /srv/smokeping/data                       # where we share data between the daemon and webapp
piddir    = /var/run                                  # filesystem directory to store PID file
cgiurl    = https://smokeping.lan.4v1.in/smokeping.fcgi  # exterior URL
smokemail = /etc/smokeping/smokemail   
tmail     = /etc/smokeping/tmail
syslogfacility = local0
# each probe is now run in its own process
# disable this to revert to the old behaviour
# concurrentprobes = no

*** Alerts ***
to = root@local
from = root@local

+someloss
type = loss
# in percent
pattern = >0%,*12*,>0%,*12*,>0%
comment = loss 3 times  in a row

*** Database ***

step     = 300
pings    = 20

# consfn mrhb steps total

AVERAGE  0.5   1  1008
AVERAGE  0.5  12  4320
    MIN  0.5  12  4320
    MAX  0.5  12  4320
AVERAGE  0.5 144   720
    MAX  0.5 144   720
    MIN  0.5 144   720

*** Presentation ***

template = /etc/smokeping/basepage.html
graphborders = no

+ charts

menu = Charts
title = The most interesting destinations
++ stddev
sorter = StdDev(entries=>4)
title = Top Standard Deviation
menu = Std Deviation
format = Standard Deviation %f

++ max
sorter = Max(entries=>5)
title = Top Max Roundtrip Time
menu = by Max
format = Max Roundtrip Time %f seconds

++ loss
sorter = Loss(entries=>5)
title = Top Packet Loss
menu = Loss
format = Packets Lost %f

++ median
sorter = Median(entries=>5)
title = Top Median Roundtrip Time
menu = by Median
format = Median RTT %f seconds

+ overview 

width = 600
height = 50
range = 10h

+ detail

width = 900
height = 400
unison_tolerance = 2
max_rtt = 0.800

"Last 3 Hours"    3h
"Last 30 Hours"   30h
"Last 10 Days"    10d
"Last 400 Days"   400d

*** Probes ***

+ FPing

binary = /usr/bin/fping

*** Targets ***

probe = FPing

menu = Top
title = Network Latency Grapher
remark = Livepeer Orchestrator Network Latency. \\
         Here we learn all about our LPT network's latency.

"""
    
    # Generate the target configuration
    for location, ips in livepeer_ips.items():
        country_code = location.split('-')[-1].upper()
        for ip in ips:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                hostname = "Unknown"

            config_output += f"++ {location} ({country_code})\n"
            config_output += f"menu = {location}\n"
            config_output += f"title = {location} / {ip} / {hostname}\n"
            config_output += f"host = {ip}\n\n"
    
    return config_output

def save_smokeping_config(config_content, filepath='/etc/smokeping/config.d/Targets'):
    """
    Save the generated Smokeping configuration to a file.

    :param config_content: String representing the Smokeping configuration content.
    :param filepath: Path to the file where the configuration should be saved.
    """
    with open(filepath, 'w') as config_file:
        config_file.write(config_content)
