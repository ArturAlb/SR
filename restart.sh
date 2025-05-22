#!/bin/bash

echo "y" | ./cleanup.sh
./generate_compose.sh
docker compose up --build
