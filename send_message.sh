#!/bin/bash

# Get all running containers with names starting with "client"
clients=($(docker ps --format '{{.Names}}' | grep '^client'))

if [ ${#clients[@]} -eq 0 ]; then
  echo "No client containers found."
  exit 1
fi

echo "Available client containers:"
for i in "${!clients[@]}"; do
  echo "$i) ${clients[$i]}"
done

# Prompt user to choose
read -p "Select a client container by number: " choice

# Validate choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 0 ] || [ "$choice" -ge "${#clients[@]}" ]; then
  echo "Invalid selection."
  exit 1
fi

selected_client="${clients[$choice]}"
echo "[+] Running client script in container: $selected_client"

docker exec -it "$selected_client" python3 volumes/client.py
