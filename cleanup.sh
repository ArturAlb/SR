#!/bin/bash

# Directories and files to clean
BUILD_DIR="./build"
COMPOSE_FILE="docker-compose.yml"

# Confirmation prompt
read -p "⚠️ This will delete $BUILD_DIR and $COMPOSE_FILE. Continue? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
  echo "❌ Cleanup canceled."
  exit 1
fi

echo "🛑 Stopping containers..."
docker compose -f "$COMPOSE_FILE" down

# Remove build directory and compose file
rm -rf "$BUILD_DIR"
rm -f "$COMPOSE_FILE"

echo "✅ Cleanup complete. Removed:"
echo " - $BUILD_DIR"
echo " - $COMPOSE_FILE"

