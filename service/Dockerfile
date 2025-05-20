FROM debian:bookworm-slim

# Install nginx and tor
RUN apt-get update && apt-get install -y nginx tor

# Copy your nginx config
COPY service/nginx.conf /etc/nginx/nginx.conf


# Expose ports
EXPOSE 80 9050

# Create a startup script
RUN echo '#!/bin/sh\n\
service nginx start\n\
# Keep the container running\n\
tail -f /dev/null' > /start.sh && \
chmod +x /start.sh

# Run the startup script
CMD ["/start.sh"]