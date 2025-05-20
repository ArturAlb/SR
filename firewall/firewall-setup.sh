#!/bin/bash

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Flush existing iptables rules
iptables -F
iptables -t nat -F
iptables -X

# Set default policies to ACCEPT
iptables -P FORWARD ACCEPT

# Allow forwarding between interfaces (adjust interface names if needed)
iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

# Keep container running to allow routing
tail -f /dev/null
