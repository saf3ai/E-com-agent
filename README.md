# Ecommerce AI Agent - Powered by Google ADK & Saf3AI

Welcome to the **Ecommerce Security AI Agent**, a robust and secure AI application built using the [Google Agent Development Kit (ADK)](https://google.github.io/google-adk/) and protected by the [Saf3AI SDK](https://saf3ai.com/).

This project demonstrates an intelligent shopping assistant capable of searching for products, generating retail recommendations, and executing simulated shopping cart transactions safely. It incorporates real-time security threat detection to protect the AI model against malicious prompts, prompt injections, and unsafe output.

---

## 🎯 Features

- **Conversational AI Intelligence**: Connects to Google's Gemini Models for deep semantic retail understanding.
- **Enterprise Security**: Native integration with Saf3AI to scan both user prompts (Input) and AI responses (Output) for safety violations.
- **Microservice Ready**: Easily deploys via Docker Compose alongside dual-channel APIs (Web UI & REST API).
- **Extensible ADK Tools**: Employs built-in custom Python tools for order tracking and cart management.

---

## 🚀 Quick Start Guide

You will need Docker Desktop installed to run this application. 

### 1. Environment Configuration

The application requires secure external API keys. We use a local environment file (`.env`) to mount these into the Docker container. 

1. Copy the provided `.env.example` in the `agent/` folder to a new `.env` file located in the root directory (where the `docker-compose.yml` lives).
   ```bash
   cp agent/.env.example .env
   ```
2. Open `.env` and configure your API keys. **(Never commit real keys to GitHub!)**

**`.env` Configuration Example:**
```env
# ── Core AI Keys ──
# Request your key from https://aistudio.google.com/
GOOGLE_API_KEY="<YOUR_GOOGLE_GEMINI_API_KEY>"

# ── Saf3AI Tracing Config (Optional) ──
SAF3AI_API_KEY="<YOUR_SAF3AI_TELEMETRY_KEY>"
SAF3AI_COLLECTOR_AGENT="<Place your collector endpoint here>"
SAF3AI_AGENT_ID="ecommerce-agent"
SAF3AI_SERVICE_NAME="ecommerce"

# ── Security Scanner Config (Required for callbacks) ──
SECURITY_SCAN_ENABLED="true"
SECURITY_API_KEY="<YOUR_SAF3AI_SCANNER_KEY>"
SECURITY_API_ENDPOINT="<Place your scanner endpoint here>"
THREAT_ACTION_LEVEL="BLOCK"
```
*(Note: If your `SECURITY_API_KEY` is a dummy placeholder, the security scanner cannot authenticate your requests and will fail open, effectively skipping security checks. You must add valid keys!)*

### 2. Building and Running the Application

Once your `.env` secrets are configured, build the application directly:

```bash
docker compose up -d --build
```

### 3. Accessing the Services

Docker handles the Interactive Chat UI, but the API Server must be started manually.

- 🎨 **Interactive Chat UI**: The ADK Web UI automatically starts at `http://localhost:8011` via Docker.

**To run the REST API Server locally**, execute the following command in your terminal:
```bash
uvicorn api.server:app --port 5000
```
- ⚙️ **REST API Interface**: Once started locally, health checks are available at `http://localhost:5000/healthz`

---

## 🛡️ Initializing Saf3AI & Security Callbacks

The Saf3AI integration protects the agent through two key initialization phases implemented natively in the code architecture.

### 1. SDK Tracing Initialization (`agent/saf3ai_setup.py`)
To monitor events, telemetry is initialized early in the runtime lifecycle. It imports `saf3ai_sdk.init()` and reads the `SAF3AI_*` variables.
```python
from saf3ai_sdk import init as saf3ai_init
saf3ai_init(
    agent_id="ecommerce-agent",
    api_key=os.getenv("SAF3AI_API_KEY"),
    safeai_collector_agent=os.getenv("SAF3AI_COLLECTOR_AGENT"),
    framework="google-adk"
)
```

### 2. Agent Security Interceptors (`agent/security.py` & `agent/main_agent.py`)
To block malicious content, security callbacks are compiled using `saf3ai_sdk.create_security_callback` and fed into the ADK Core agent.
```python
# Create the callback interceptors
before_cb, after_cb = create_security_callback(
    api_endpoint=os.getenv("SECURITY_API_ENDPOINT"),
    api_key=os.getenv("SECURITY_API_KEY"),
    on_scan_complete=security_policy,
    scan_responses=True,
    agent_identifier="ecommerce_agent"
)

# Connect them to the Agent Core
ecommerce_agent = Agent(
    model="gemini-2.5-pro",
    tools=[...],
    before_model_callback=before_cb,
    after_model_callback=after_cb
)
```
*(If you bypass placing a `SECURITY_API_KEY`, or leave the dummy `placeholder` value, the callbacks will instantiate but the underlying network request to the `scanner-dev` endpoint will reject the scan, meaning security acts as if it is not enabled!)*

---

## 🧹 Tearing Down

To gracefully shut off the systems after usage:

```bash
docker compose down
```
