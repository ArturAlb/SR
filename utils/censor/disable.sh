#!/bin/sh
set -e

iptables -F FORWARD
iptables -P FORWARD ACCEPT

echo "Censorship disabled: all FORWARD rules flushed, policy set to ACCEPT."

