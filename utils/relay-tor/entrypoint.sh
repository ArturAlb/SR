#!/bin/bash

# Tells every node that the client is accessible through the censor box
ip route add 11.1.0.0/16 via 10.1.0.253

echo "Installing cryptography"
pip install cryptography > /dev/null 2>&1



exec python3 /volumes/ssl_serv.py --mode tor
