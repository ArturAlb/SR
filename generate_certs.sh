#!/bin/bash

echo "[*] Generating certificates for all components in docker-compose.yml"
COMPOSE_FILE="docker-compose.yml"
TEMP_DIRECTORY_JSON="directory.json"
CERTS_JSON_ENTRIES=()

# Convert YAML to JSON (yq python version uses -y to preserve YAML)
yq -y '.' "$COMPOSE_FILE" > compose.json

# Extract service names using Python
SERVICE_NAMES=$(python3 -c "
import sys, yaml
with open('compose.json') as f:
    data = yaml.safe_load(f)
services = data.get('services', {})
print(' '.join(services.keys()))
")

for service in $SERVICE_NAMES; do
  if [[ "$service" == *client* || "$service" == "censor" ]]; then
    echo "[!] Skipping $service"
    continue
  fi

  echo "[+] Generating cert for $service"

  # Get IP using Python
  IP=$(python3 -c "
import sys, yaml
with open('compose.json') as f:
    data = yaml.safe_load(f)
ip = data['services']['$service'].get('networks', {}).get('tor_net', {}).get('ipv4_address', '')
print(ip)
  ")

  if [[ -z "$IP" ]]; then
    echo "[!] No IP found for $service, skipping"
    continue
  fi

  # Determine type
  if [[ "$service" == relay* ]]; then
    TYPE="relay"
  elif [[ "$service" == exit* ]]; then
    TYPE="exit"
  else
    TYPE="unknown"
  fi

  # Create cert directory
  CERT_DIR="build/$service/volumes/certs"
  mkdir -p "$CERT_DIR"

  # Generate cert
  openssl req -x509 -newkey rsa:2048 \
    -keyout "$CERT_DIR/cert.key" \
    -out "$CERT_DIR/cert.crt" \
    -days 365 \
    -nodes \
    -subj "/CN=$service"

  # Encode the cert in base64
  CERT_BASE64=$(base64 -w 0 "$CERT_DIR/cert.crt")

  ENTRY="{\"name\": \"$service\", \"type\": \"$TYPE\", \"ip\": \"$IP\", \"cert_base64\": \"$CERT_BASE64\"}"
  CERTS_JSON_ENTRIES+=("$ENTRY")
done

# Output directory.json
echo "[" > "$TEMP_DIRECTORY_JSON"
printf "  %s\n" "$(IFS=,; echo "${CERTS_JSON_ENTRIES[*]}")" >> "$TEMP_DIRECTORY_JSON"
echo "]" >> "$TEMP_DIRECTORY_JSON"

# Copy to client(s)
for client_dir in build/*client*/; do
  cp "$TEMP_DIRECTORY_JSON" "${client_dir}volumes/"
done

# Clean up
rm compose.json "$TEMP_DIRECTORY_JSON"
echo "[✓] Certificates and directory.json generated!"

