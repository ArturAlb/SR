#!/bin/bash

echo "[*] Generating certificates for all components in build/ (except 'censor')"

# Iterate through all directories inside build/
for dir in build/*/; do
  # Get base name (e.g., relay1, exit1, etc.)
  name=$(basename "$dir")

  # Skip 'censor' directory
  if [ "$name" == "censor" ]; then
    echo "[!] Skipping $name"
    continue
  fi

  echo "[+] Generating certificate for $name"

  # Create certs directory if it doesn't exist
  mkdir -p "$dir/volumes/certs"

  # Generate cert and key with standardized names
  openssl req -x509 -newkey rsa:2048 \
    -keyout "$dir/volumes/certs/cert.key" \
    -out "$dir/volumes/certs/cert.crt" \
    -days 365 \
    -nodes \
    -subj "/CN=$name"
done

echo "[✓] All certificates generated as cert.key and cert.crt."

