#!/bin/sh

set -e

# enable IP forwarding
#sysctl -w net.ipv4.ip_forward=1

# drop all traffic from client_net -> tor_net relays
for ip in 10.1.0.2 10.1.0.3 10.1.0.4 10.1.0.5 10.1.0.6 10.1.0.7; do
    iptables -A FORWARD -s 10.1.2.0/24 -d $ip -j DROP
done

# allow everything else
iptables -A FORWARD -s 10.1.2.0/24 -d 0.0.0.0/0 -j ACCEPT
iptables -A FORWARD -s 0.0.0.0/0 -d 10.1.2.0/24 -j ACCEPT

# keep container alive so iptables rules persist
tail -f /dev/null
