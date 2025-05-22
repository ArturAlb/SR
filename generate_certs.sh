#!/bin/bash

# List of relay names
relays=(relay exit hidden_service)

# Create certs for each relay
for relay in "${relays[@]}"; do
  echo "[+] Generating certificate for $relay"

  mkdir -p ./utils/$relay/certs

  openssl req -x509 -newkey rsa:2048 \
    -keyout ./utils/$relay/certs/$relay.key \
    -out ./utils/$relay/certs/$relay.crt \
    -days 365 \
    -nodes \
    -subj "/CN=./utils/$relay"
done

echo "[✓] All certificates generated."

