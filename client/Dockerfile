FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y tor curl iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY client/client-setup.sh /usr/local/bin/client-setup.sh
RUN chmod +x /usr/local/bin/client-setup.sh

CMD ["/usr/local/bin/client-setup.sh"]
