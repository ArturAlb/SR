FROM ubuntu:latest

RUN apt-get update && apt-get install -y iproute2 iptables iputils-ping

# Enable IP forwarding and set iptables rules at container startup
COPY firewall/firewall-setup.sh /usr/local/bin/firewall-setup.sh
RUN chmod +x /usr/local/bin/firewall-setup.sh

ENTRYPOINT ["/usr/local/bin/firewall-setup.sh"]
