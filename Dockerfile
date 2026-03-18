FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8011

WORKDIR /app

# System deps (kept minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Expose ports for both the UI and the API Server
EXPOSE 8011
EXPOSE 5000

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Run both the web UI and the API server using the startup script
CMD ["/app/start.sh"]
