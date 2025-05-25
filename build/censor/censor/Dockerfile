FROM handsonsecurity/seed-ubuntu:large

RUN mkdir -p /censor
RUN touch /var/log/censor.txt

COPY ./censor/censor.py /censor/censor.py
COPY ./censor/entrypoint.sh /censor/entrypoint.sh

# Install required packages
RUN apt-get update && apt-get install -y \
    iptables \
    libnfnetlink0 \
    libnetfilter-queue1 \
    gcc \
    libnetfilter-queue-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install scapy netfilterqueue

ENTRYPOINT ["/censor/entrypoint.sh"]

