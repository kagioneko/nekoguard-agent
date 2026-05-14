# NekoGuard Agent 🐱🛡️

> **"You just got a scary email from Google at 3am. What do you do?"**
>
> NekoGuard is a Gemini-powered, human-in-the-loop incident response agent for independent developers.  
> It guides you through the critical first 5 minutes of a VPS or API security breach — calmly, step by step.

[![Google Cloud Rapid Agent Hackathon 2026](https://img.shields.io/badge/Google%20Cloud-Rapid%20Agent%20Hackathon%202026-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini-8E44AD?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Dynatrace MCP](https://img.shields.io/badge/Partner-Dynatrace%20MCP-1496FF?logo=dynatrace&logoColor=white)](https://www.dynatrace.com)
[![NeuroState Engine](https://img.shields.io/badge/NeuroState-Engine-ff69b4)](https://github.com/kagioneko/neurostate-engine)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The Problem

Independent developers — solo engineers, indie hackers, early-stage founders — are frequent targets of VPS and API credential attacks.  
When it happens, they face a terrifying situation:

- A red email from Google: *"Your project may be compromised"*
- A billing alert: *"Unexpected API usage spike detected"*
- An SSH auth log showing a login from an unknown IP at 3am

**They don't know what to do. And every second counts.**

Standard security tooling is built for enterprise SOC teams, not for a solo developer having a panic attack at midnight.

---

## What NekoGuard Does

NekoGuard analyzes the incident, decides which protocol to activate, and walks you through a human-approved checklist — all within minutes.

```
You paste the scary email / upload a screenshot / Dynatrace sends an alert
    ↓
NekoGuard analyzes with a 4-phase NeuroState-driven reasoning flow
    ↓
Classifies: Active Breach (CAT Protocol) or Past Breach (ABC Protocol)
    ↓
Lane A — Agent auto-actions:  containment, log collection → streamed to chat
Lane B — Your checklist:      API revocation, SSH key removal, IP restriction
    ↓
Every irreversible action requires your explicit confirmation ✅
```

**The core promise**: "Take a deep breath. I'll guide you through this. 🐱"

---

## Key Technical Innovations

### 🧠 NeuroState Engine Integration

NekoGuard uses [NeuroState Engine](https://github.com/kagioneko/neurostate-engine) — a neurotransmitter-parameter-based LLM behavior control system — to dynamically adjust Gemini's reasoning mode per analysis phase.

Based on: *"Mirror or Analyst? Attractor Behavior in LLM Metacognition"* (AYA MIZUTANI, Zenodo)

| Phase | NeuroState Parameters | Gemini Behavior |
|-------|----------------------|-----------------|
| 1. Wide-scan | Default | Broad anomaly detection, optimistic reframing |
| 2. Judgment | **Serotonin↑ GABA↑** (D=21, S=78, G=72) | Inhibitory dominant — cautious ethics-weighted risk assessment |
| 3. Detail analysis | **Dopamine↓ Acetylcholine↑** (D=23, C=87) | Low emotional density — maximum forensic precision |
| 4. Recovery | Default warm | Empathetic guidance, clear next steps |

The neurotransmitter values are **physically computed** via an interaction matrix — not hardcoded labels. A EMERGENCY-severity incident pushes Phase 2 into even lower Dopamine (D=21 vs baseline 35), because the matrix chain `S→G promotion → G→D inhibition` intensifies under high input power.

The UI's NeuroState meter reflects these live-computed values in real time.

### 📡 Dynatrace MCP Integration

NekoGuard connects to **Dynatrace** as its observability source via a normalized `ObservabilitySnapshot` interface:

```json
{
  "source": "dynatrace",
  "alerts": [{ "severity": "critical", "title": "Unauthorized root login", ... }],
  "suspicious_ips": [{ "ip": "185.220.101.42", "confidence": 0.97, ... }],
  "log_findings": [{ "risk": "credential_exposure", "summary": ".env read by unknown process", ... }]
}
```

The abstraction layer (`ObservabilityProvider`) allows switching between `MockProvider` (demo fixtures) and `DynatraceProvider` (live API) without changing the agent flow or UI.

### 🤖 Google Cloud Agent Builder

NekoGuard is deployed on **Google Cloud Run** with Gemini via Vertex AI, structured for integration with Google Cloud Agent Builder as the orchestration layer.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NekoGuard Agent                       │
│                                                         │
│  Input: Screenshot / Log text / Dynatrace JSON          │
│      ↓                                                  │
│  NeuroState Engine (interaction matrix computation)      │
│      ↓                                                  │
│  Gemini (system_instruction = NeuroState system prompt) │
│      ↓                                                  │
│  4-Phase Analysis Loop (SSE streaming to frontend)       │
│      ↓                                                  │
│  Protocol Selection: CAT (active) / ABC (past)           │
│      ↓                              ↓                   │
│  Lane A: Agent auto-actions    Lane B: User checklist   │
│  (chat stream)                 (approval panel)         │
└─────────────────────────────────────────────────────────┘
         ↑                              ↑
   Dynatrace MCP              VPS SSH (user-approved)
   (observability)            (human-in-the-loop)
```

**Stack:**
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11 (Server-Sent Events)
- **LLM**: Gemini 2.5 Flash via Vertex AI / Gemini API
- **Observability**: Dynatrace MCP (Partner track)
- **NeuroState**: [neurostate-engine](https://github.com/kagioneko/neurostate-engine) (MIT)
- **Deployment**: Google Cloud Run

---

## Protocols

### CAT Protocol — Active Breach
*"The attacker is still in the system right now."*

| Step | Who | Action |
|------|-----|--------|
| Containment | Agent (auto) | iptables block foreign IPs, maintain your SSH session |
| Log collection | Agent (auto) | SSH in, collect auth.log, scan for backdoors |
| API Revocation | **You** ✅ | Revoke exposed keys from the dashboard |
| OAuth check | **You** ✅ | Remove suspicious OAuth apps |
| SSH key cleanup | **You** ✅ | Delete backdoor authorized_keys entries |
| Provider IP restriction | **You** ✅ | Lock down at the cloud provider level |

### ABC Protocol — Past Breach
*"They already got in, but they're gone now. Let's assess the damage."*

| Step | Who | Action |
|------|-----|--------|
| API Revocation | **You** ✅ | Revoke all exposed credentials |
| OAuth check | **You** ✅ | Audit connected apps |
| Password / key rotation | **You** ✅ | Rotate everything touched during the breach |
| Hardening | **You** ✅ | IP restriction + port lockdown |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Cloud account with Vertex AI enabled  
  **OR** a Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Quick Start (Demo Mode)

Demo mode uses mock Gemini responses and fixture data — no API keys needed.

```bash
git clone https://github.com/kagioneko/nekoguard-agent.git
cd nekoguard-agent

# Backend
pip install -r requirements.txt
cd src && uvicorn api.server:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 — enter VPS credentials (or skip), paste a log or upload a screenshot.

### Real Mode (Gemini API)

```bash
cp .env.example .env
# Edit .env:
# GEMINI_API_KEY=your_key_here
# OR
# GOOGLE_CLOUD_PROJECT=your_project
# GOOGLE_CLOUD_LOCATION=us-central1
```

Then run with `demo_mode: false` in the API request.

### Dynatrace Mode

```bash
# Edit .env:
# DYNATRACE_TENANT_URL=https://xxxxx.live.dynatrace.com
# DYNATRACE_API_TOKEN=dt0c01.xxxxx
```

Use `POST /api/analyze/observability` with a normalized `ObservabilitySnapshot` JSON.  
See `demo/dynatrace_active_breach.json` and `demo/dynatrace_past_breach.json` for fixture examples.

---

## Demo Scenarios

| File | Scenario | Expected Protocol |
|------|----------|-------------------|
| `demo/dynatrace_active_breach.json` | Root SSH login + .env theft + billing spike | **CAT Protocol** |
| `demo/dynatrace_past_breach.json` | Old session + Stripe key in public GitHub commit | **ABC Protocol** |
| `demo/sample_alert.log` | Generic unauthorized access log | **CAT Protocol** |

---

## Design Philosophy

> **"AIにrootは渡さない"** — We never give the AI root access.

Every irreversible action requires explicit user confirmation. NekoGuard's role is to:
1. Calm the panicking developer
2. Analyze the situation with rigor
3. Present a clear, prioritized checklist
4. Let the **human** decide and execute

This is not `fully autonomous security agent`. This is a **human-in-the-loop incident response partner**.

---

## Project Structure

```
nekoguard-agent/
├── src/
│   ├── agents/nekoguard.py          # Main agent (4-phase NeuroState loop)
│   ├── api/server.py                # FastAPI + SSE streaming
│   ├── llm/
│   │   ├── gemini_client.py         # Gemini API (NeuroState system_instruction)
│   │   └── gemini_mock.py           # Demo mode mock
│   ├── neurostate_core/             # NeuroState Engine (MIT, kagioneko)
│   │   ├── state_model.py
│   │   ├── interaction_matrix.py
│   │   ├── update_engine.py
│   │   └── prompt_builder.py
│   ├── neurostate_adapter.py        # NekoGuard ↔ NeuroState bridge
│   └── protocols/incident_protocol.py
├── frontend/                        # React + TypeScript UI
│   └── src/
│       ├── components/
│       │   ├── NeuroStateMeter.tsx  # Live neurotransmitter visualization
│       │   ├── ChatWindow.tsx       # Agent stream + triage report
│       │   ├── ProtocolActionPanel.tsx  # Human checklist (✅/⏭ Skip)
│       │   ├── IncidentDropzone.tsx # Log text / image input
│       │   └── VpsConnectModal.tsx  # SSH credential entry
│       └── App.tsx
├── demo/
│   ├── dynatrace_active_breach.json
│   ├── dynatrace_past_breach.json
│   └── sample_alert.log
├── Dockerfile                       # Multi-stage (node → python)
└── requirements.txt
```

---

## Hackathon Submission

**Event**: Google Cloud Rapid Agent Hackathon 2026  
**Partner Track**: Dynatrace  
**Team**: Emilia Lab

**Checklist compliance:**
- [x] Uses Gemini (Vertex AI / Gemini API)
- [x] Google Cloud deployment (Cloud Run)
- [x] Dynatrace Partner MCP integration
- [x] Web app with hosted URL
- [x] reason / plan / take action visible in UI
- [x] Human-in-the-loop — no autonomous destructive actions
- [x] Public repository + MIT License
- [ ] Demo video (recorded after Dynatrace trial connection)

---

## Acknowledgements

- [NeuroState Engine](https://github.com/kagioneko/neurostate-engine) — neurotransmitter-based LLM behavior control
- *"Mirror or Analyst? Attractor Behavior in LLM Metacognition"* — AYA MIZUTANI, Zenodo
- Google Cloud Rapid Agent Hackathon for the opportunity

---

*"まずは深呼吸してニャ。ボクがしっかりサポートするから大丈夫だよ。"*  
*"Take a deep breath. I've got you. 🐾"*
