# Setup Guide for NekoGuard Agent

## 1. Prerequisites
- Python 3.9+
- A Google Cloud Project with Gemini API access
- A Dynatrace environment (for log monitoring)

## 2. API Keys and Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

### Gemini API
Get your API key from Google AI Studio or Google Cloud Console and set `GEMINI_API_KEY`.

### Dynatrace MCP Setup
1. Log in to your Dynatrace tenant.
2. Go to **Access Tokens** and generate a new token with `logs.read` scope.
3. Set `DYNATRACE_TENANT_URL` and `DYNATRACE_API_TOKEN` in `.env`.

## 3. Running NekoGuard
You can run NekoGuard in two modes:

### Demo Mode (API Keys not strictly required)
Runs using local mock data and simulated Gemini responses. Perfect for safe evaluation.
```bash
python src/agents/nekoguard.py --demo
```

### Real Mode
Connects to actual Dynatrace logs and the real Gemini 3 API.
```bash
python src/agents/nekoguard.py --real
```
