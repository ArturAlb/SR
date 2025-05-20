#!/bin/bash

# Set default gateway to firewall
ip route add default via 172.18.0.254

# Start Tor in background
tor &

# Wait for Tor to start
sleep 10

# Example: curl through Tor SOCKS proxy to check IP
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org

export http_proxy="socks5://172.18.0.20:9050"
export https_proxy="socks5://172.18.0.20:9050"

# Keep container running
tail -f /dev/null
