#!/bin/bash

# List of relay names
relays=(exit1 exit2 hidden_service)

# Create certs for each relay
for relay in "${relays[@]}"; do
  echo "[+] Generating certificate for $relay"

  mkdir -p $relay/certs

  openssl req -x509 -newkey rsa:2048 \
    -keyout $relay/certs/$relay.key \
    -out $relay/certs/$relay.crt \
    -days 365 \
    -nodes \
    -subj "/CN=$relay"
done

echo "[✓] All certificates generated."

