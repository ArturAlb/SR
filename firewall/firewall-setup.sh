#!/bin/bash

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Flush existing rules
iptables -F
iptables -t nat -F
iptables -X

# Default policies
iptables -P FORWARD DROP
iptables -P INPUT DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# --- Network Segmentation Rules ---
# Allow established/related traffic
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow client → Tor proxy (SOCKS5)
iptables -A FORWARD -i eth0 -o eth0 -s 172.18.1.0/24 -d 172.18.1.20 -p tcp --dport 9050 -j ACCEPT

# Allow Tor proxy → Hidden service (Tor network)
iptables -A FORWARD -i eth1 -o eth1 -s 172.18.2.20 -d 172.18.2.30 -p tcp --dport 9001 -j ACCEPT

# Block all other client → global traffic
iptables -A FORWARD -s 172.18.1.0/24 -d 172.19.0.0/24 -j LOG --log-prefix "BLOCKED_CLIENT_GLOBAL: "
iptables -A FORWARD -s 172.18.1.0/24 -d 172.19.0.0/24 -j DROP



# Keep container running
tail -f /dev/null