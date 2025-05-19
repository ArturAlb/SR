# suricata/Dockerfile
FROM jasonish/suricata:latest

# Copy your custom rules later if needed
COPY ./censor/config/suricata.yaml /etc/suricata/suricata.yaml
COPY ./censor/config/rules/ /etc/suricata/rules/
