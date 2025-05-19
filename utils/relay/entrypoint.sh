#!/bin/bash

# Tells every node that the client is accessible through the censor box
ip route add 11.1.0.0/16 via 10.1.0.253

pip install cryptography

# Keep container alive
exec bash
