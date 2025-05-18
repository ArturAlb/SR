#!/bin/sh
set -e

# Delete existing default route and add a new one
ip route del default
ip route add default via 10.10.1.2

# Execute the container's default command
exec "$@"
