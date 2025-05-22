#!/bin/bash

echo "Checking network routes:"
ip route show
echo -e "\n"
#Start Tor in background
tor &

# Wait for Tor to start
sleep 10

# Example: curl through Tor SOCKS proxy to check IP

ip route replace default via 172.18.1.200

export http_proxy="socks5://172.18.0.20:9050"
export https_proxy="socks5://172.18.0.20:9050"

# Reroute traffic for tor_net to suricata

tail -f /dev/null
