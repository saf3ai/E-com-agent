FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8011

WORKDIR /app

# System deps (kept minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Expose port for the UI
EXPOSE 8011

# Setup isolated agent directory
RUN mkdir -p /tmp/adk_apps && ln -sf /app/agent /tmp/adk_apps/e-commerce-agent

# Run only the ADK web UI
CMD ["adk", "web", "/tmp/adk_apps", "--port", "8011", "--host", "0.0.0.0"]
