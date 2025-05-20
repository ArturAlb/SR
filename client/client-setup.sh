#!/bin/bash

# Replace default route to use firewall container IP (assumes 172.18.0.254)
ip route replace default via 172.18.0.254

# Keep container alive
tail -f /dev/null
