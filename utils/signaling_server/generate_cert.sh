#!/bin/bash
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -keyout certs/signaling.key -out certs/signaling.crt -days 365 -nodes -subj "/CN=localhost"
