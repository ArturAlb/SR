#!/bin/bash
set -e

echo "[*] Setting up iptables rule for NFQUEUE..."
iptables -I FORWARD -i eth0 -j NFQUEUE --queue-num 1

echo "[*] Starting censorship script..."
exec python3 /censor/censor.py
