FROM debian:bookworm-slim

# Install nginx and tor
RUN apt-get update && apt-get install -y nginx tor

# Copy your nginx config (optional, default serves /var/www/html)
COPY service/nginx.conf /etc/nginx/nginx.conf

# Copy your torrc config
COPY service/torrc /etc/tor/torrc

# Expose nginx port internally (not mapped to host)
EXPOSE 80

# Start nginx and tor
CMD service nginx start && tor -f /etc/tor/torrc
