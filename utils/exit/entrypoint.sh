#!/bin/bash

# Tells every node that the client is accessible through the censor box
ip route add 11.1.0.0/16 via 10.1.0.253

pip install cryptography > /dev/null 2>&1
pip install aiortc > /dev/null 2>&1
pip install requests > /dev/null 2>&1

# Keep container alive
exec python3 /relay/print_message.py 
