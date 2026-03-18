#!/bin/bash
# Start the API server in the background on port 5000
echo "Starting API Server on port 5000..."
gunicorn -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:5000 api.server:app &

# Start the ADK web UI in the foreground on port 8011
echo "Starting ADK Web UI on port 8011..."
# Isolate the agent discovery so the UI dropdown only shows "e-commerce-agent"
export PYTHONPATH=/app
mkdir -p /tmp/adk_apps
ln -sf /app/agent /tmp/adk_apps/e-commerce-agent

export HOST=0.0.0.0
export PORT=8011
adk web /tmp/adk_apps --port 8011 --host 0.0.0.0
