#!/bin/bash

echo "y" | ./cleanup.sh
./generate_compose.sh
./generate_certs.sh
docker compose up --build
