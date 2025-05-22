FROM python:3.9-slim
WORKDIR /app

# Disable pip progress bar to avoid threading issues in low-resource Docker environments
ENV PIP_PROGRESS_BAR=off

COPY . .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8443
CMD ["gunicorn", "--certfile=/app/certs/cert.pem", "--keyfile=/app/certs/key.pem", "-b", "0.0.0.0:8443", "signaling_server:app"]