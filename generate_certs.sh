#!/bin/bash

echo "[*] Generating certificates for all components in build/"

DIRECTORY_FILE_NAME="directory.json"
TEMP_ENTRIES=()

# Iterate through all directories inside build/
for dir in build/*/; do
  # Get base name (e.g., relay1, exit1, etc.)
  name=$(basename "$dir")

  # Skip 'censor' directory
  if [[ "$name" == "censor" || "$name" == *client* ]]; then
    echo "[!] Skipping $name"
    continue
  fi

  echo "[+] Generating certificate for $name"

  # Create certs directory if it doesn't exist
  mkdir -p "${dir}volumes/certs"

  # Generate cert and key with standardized names
  openssl req -x509 -newkey rsa:2048 \
    -keyout "${dir}volumes/certs/cert.key" \
    -out "${dir}volumes/certs/cert.crt" \
    -days 365 \
    -nodes \
    -subj "/CN=$name"

  # Read and base64-encode the cert
  CERT_CONTENT=$(base64 -w 0 "${dir}volumes/certs/cert.crt")

  # Detect type 
  if [[ "$name" == relay* ]]; then
    TYPE="relay"
  elif [[ "$name" == exit* ]]; then
    TYPE="exit"
  else
    TYPE="unknown"
  fi

  # Create a JSON entry
  ENTRY="{\"name\": \"$name\", \"type\": \"$TYPE\", \"cert_base64\": \"$CERT_CONTENT\"}"
  TEMP_ENTRIES+=("$ENTRY")
done

# Join entries into a JSON array
echo "[" > "$DIRECTORY_FILE_NAME"
printf "  %s\n" "$(IFS=,; echo "${TEMP_ENTRIES[*]}")" >> "$DIRECTORY_FILE_NAME"
echo "]" >> "$DIRECTORY_FILE_NAME"

# Copy file to clients
for dir in build/*/; do
  # Get base name 
  name=$(basename "$dir")

  if [[ "$name" == *client* ]]; then
      cp "./$DIRECTORY_FILE_NAME" "${dir}volumes/"
  fi
done

# Remove the original directory file
rm "./$DIRECTORY_FILE_NAME"

echo "[✓] All certificates generated."
echo "[✓] Directory file created." 
