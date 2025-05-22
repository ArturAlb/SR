fROM alpine:latest

RUN apk add --no-cache tor curl

COPY torrc /etc/tor/torrc

EXPOSE 9050

USER tor

CMD /bin/sh -c "tor -f /etc/tor/torrc"

