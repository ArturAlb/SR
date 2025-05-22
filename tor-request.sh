#!/bin/bash

# Fetch the .onion address from the Tor proxy container
ONION_ADDRESS=$(docker exec sr-hidden-service-1 cat /var/lib/tor/hidden_service/hostname 2>/dev/null)

# Check if the onion address was retrieved successfully
if [ -z "$ONION_ADDRESS" ]; then
    echo "ERROR: Failed to get .onion address from Tor proxy."
    echo "Make sure:"
    echo "1. The 'sr-hidden-service-1' container is running"
    echo "2. Hidden service is configured in torrc"
    echo "3. The hostname file exists in /var/lib/tor/hidden_service/"
    exit 1
fi

echo "Discovered .onion address: $ONION_ADDRESS"
echo "Making request through Tor proxy..."

# Make the curl request through the client container
docker exec sr-client-1 curl --socks5-hostname 172.18.2.20:9050 -v "http://$ONION_ADDRESS"
