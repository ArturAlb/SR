#!/bin/bash

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Flush all existing rules
iptables -F
iptables -t nat -F
iptables -X

# Default: DROP all forwarding by default
iptables -P FORWARD DROP

# Allow return traffic (global -> country)
iptables -A FORWARD -i eth1 -o eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow Tor outbound ports from country to anywhere (adjust as needed)
iptables -A FORWARD -s 172.18.0.0/16 -p tcp --dport 9001 -j ACCEPT
iptables -A FORWARD -s 172.18.0.0/16 -p tcp --dport 9050 -j ACCEPT
iptables -A FORWARD -s 172.18.0.0/16 -p tcp --dport 9051 -j ACCEPT

# Log attempts before dropping (optional)
iptables -A FORWARD -s 172.18.0.0/16 -d 172.19.0.0/16 -j LOG --log-prefix "Blocked country → global: "

# Drop all other direct traffic from country to global
iptables -A FORWARD -s 172.18.0.0/16 -d 172.19.0.0/16 -j DROP

# Mirror traffic to Suricata
iptables -I FORWARD -j NFQUEUE --queue-num 0

# Block based on Suricata alerts (assuming Suricata uses NFQ)
iptables -A INPUT -j NFQUEUE --queue-num 0
iptables -A OUTPUT -j NFQUEUE --queue-num 0

# Keep container alive
tail -f /dev/null
