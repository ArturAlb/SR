#!/bin/bash

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Flush all existing rules
iptables -F
iptables -t nat -F
iptables -X

# ✅ Default: DROP everything by default
iptables -P FORWARD DROP

# ✅ Allow return traffic (global to country)
iptables -A FORWARD -i eth1 -o eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT

# ❌ Block all country → global traffic (172.18.x → 172.19.x)
iptables -A FORWARD -s 172.18.0.0/16 -d 172.19.0.0/16 -j DROP

# 🧪 Optional: Log dropped attempts
iptables -A FORWARD -s 172.18.0.0/16 -d 172.19.0.0/16 -j LOG --log-prefix "Blocked country → global: "

# Keep container alive
tail -f /dev/null
