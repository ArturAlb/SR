#!/bin/bash

# Tells the client that the relays are through the censor box
ip route add 10.1.0.0/16 via 11.1.0.254

pip install cryptography

# Keep container alive
exec bash
