#!/bin/bash

# Tells the client that the relays are through the censor box
ip route add 10.1.0.0/16 via 11.1.0.254

pip install cryptography > /dev/null 2>&1
pip install aiortc > /dev/null 2>&1
pip install requests > /dev/null 2>&1

# Keep container alive
cd /client
python3 test.py
# Keep container alive after script finishes
exec tail -f /dev/null
