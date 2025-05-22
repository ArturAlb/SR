# ./suricata/Dockerfile
FROM debian:bookworm

# Install Suricata, iptables, and networking tools
RUN apt-get update && \
    apt-get install -y tcpdump suricata iptables iproute2 net-tools procps && \
    apt-get clean

# Create config and log dirs (if needed)
RUN mkdir -p /etc/suricata /var/log/suricata

# Copy config at build time if you want, or mount it via volume at runtime
# COPY ./config /etc/suricata/
# COPY ./rules /etc/suricata/rules/

# Entry command, same logic as before
CMD /bin/sh -c "\
  iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE && \
  suricata -i eth0 -c /etc/suricata/suricata.yaml -S /etc/suricata/rules/tor.rules"

