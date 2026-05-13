# NekoGuard Agent - Technical Specification

> Incident Response AI Agent for Non-Expert Developers  
> Google Cloud Rapid Agent Hackathon submission

---

## Overview

NekoGuard Agent is an AI-powered incident response agent for developers who experience credential/server compromise and don't know what to do next.

**Core concept**: "The first 5 minutes matter most."  
Stopping billing and revoking API keys before investigating prevents the majority of financial damage.

**Target persona**: Beginner developers who just received a scary red email and are about to panic.

---

## Architecture

### Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | Google Cloud Agent Builder |
| Primary LLM | Gemini 3 (required by hackathon) |
| Multimodal Input | Gemini Vision (screenshot analysis) |
| Monitoring | Dynatrace MCP |
| Execution Layer | Claude Code (VPS-side) |
| State Management | NeuroState Engine |

### Deployment Model

```
Google Cloud (NekoGuard Agent)
    ↓ Dynatrace MCP
    ↓ VPS monitoring data (real-time)
    ↓ Anomaly detection
    ↓ SSH → VPS Containment execution
```

**Key design principle**: Agent runs externally (Google Cloud), NOT inside the VPS.  
Reason: If VPS is compromised, the agent survives and remains operational.  
（実体験から：侵害されたVPS内のツールは使えなかった）

---

## Protocol Design

### Dynamic Protocol Selection

NekoGuard selects protocol based on breach status:

| Situation | Protocol | Flow |
|-----------|----------|------|
| Active breach (ongoing) | **CAT Protocol** | Containment → API revocation → Triage |
| Past breach (already happened) | **ABC Protocol** | API revoke → Backup credentials → Containment |

### CAT Protocol (Active Breach)

```
C - Containment
    → Restrict SSH access to personal IP only
    → Block suspicious IPs detected by Dynatrace

A - API Revocation
    → Immediately disable compromised API keys
    → Revoke OAuth tokens

T - Triage
    → Query logs via Dynatrace MCP (DQL)
    → Generate incident report with damage assessment
    → Estimate financial impact
```

### ABC Protocol (Past Breach)

```
A - API Revoke
    → Disable all potentially compromised credentials first

B - Backup Credentials
    → Secure known-good credentials before anything else

C - Containment
    → Restrict access, harden configuration
```

---

## NeuroState Integration

### Alert Levels

NeuroState Engine manages agent state through 3 levels:

| Level | Trigger | Agent Behavior |
|-------|---------|----------------|
| NORMAL | No anomaly | Monitoring mode, low intervention |
| ALERT | Suspicious activity detected | Heightened analysis, user notification |
| EMERGENCY | Active breach confirmed | Full CAT Protocol execution, aggressive containment |

### Phase-Based Parameter Control

**Core innovation**: NeuroState parameters dynamically adjust Gemini 3's semantic trajectory per phase, simulating different "thinking modes" within a single model.

Based on findings from:  
*"Mirror or Analyst? Attractor Behavior in LLM Metacognition" (AYA MIZUTANI, Zenodo)*

| Phase | Role | NeuroState Direction | Target Behavior |
|-------|------|----------------------|-----------------|
| Wide-area scan | Anomaly detection | Default Gemini | Broad pattern recognition, optimistic reframing for initial triage |
| Judgment phase | Risk assessment | Serotonin↑ GABA↑ | Cautious, ethics-weighted, Claude-like deliberation |
| Detail analysis | Technical forensics | Dopamine↓ Acetylcholine↑ | Low emotional density, high technical precision, Codex-like |
| Recovery phase | User guidance | Default Gemini | Natural positive reframing, constructive next-step guidance |

**Why this works**: Different LLM models exhibit relatively stable "semantic attractors" — characteristic paths through meaning space. NeuroState prompt parameters can nudge Gemini toward adjacent attractor regions without switching models.

This is a prompt-design hypothesis, not a claim about model internals.

---

## Input Methods

### 1. Screenshot / Multimodal Input
- User pastes scary email screenshot
- Gemini Vision extracts: alert type, affected services, timestamps, IP addresses
- Automatic severity classification → NeuroState level assignment

### 2. Natural Language Description
- "I got a red email from Google"
- "Someone is using my API key"
- "My VPS bill is exploding"

### 3. Log Input (via Dynatrace MCP)
- Real-time log query via DQL
- Anomaly pattern detection
- Automatic IP flagging

---

## Agent Flow

```
User Input (screenshot / text / log)
    ↓
Gemini Vision analysis
    ↓
NeuroState: severity assessment → NORMAL / ALERT / EMERGENCY
    ↓
Protocol selection: CAT (active) or ABC (past)
    ↓
[Phase 1] Wide-scan: Gemini default mode
    → Identify affected services
    → Estimate breach scope
    ↓
[Phase 2] Judgment: Claude-like mode (Serotonin↑ GABA↑)
    → Risk assessment
    → Action priority ranking
    → Irreversible action confirmation
    ↓
[Phase 3] Detail analysis: Codex-like mode (AC↑ D↓)
    → Log forensics via Dynatrace MCP
    → Technical damage assessment
    → Evidence collection
    ↓
[Phase 4] Recovery: Gemini natural mode
    → Step-by-step recovery checklist
    → Dynamic checklist (updates as user completes steps)
    → Incident report generation
    ↓
Claude Code (VPS-side execution layer)
    → Receives natural language instructions from NekoGuard
    → Executes: SSH restriction, credential rotation, hardening
```

---

## Parallel Processing Design

While agent analyzes in background, user receives:
- Immediate action checklist (what to do RIGHT NOW)
- Dynamic updates as analysis completes
- Progress indicator

User handles immediate actions simultaneously with agent analysis → reduces critical first-5-minute window.

---

## Implementation Phases

### Phase 1 (Hackathon MVP)
- [ ] Single-agent mode (Gemini 3, no team)
- [ ] Screenshot input via Gemini Vision
- [ ] CAT Protocol execution
- [ ] NeuroState 3-level alert system
- [ ] Dynatrace MCP integration (log query + anomaly detection)
- [ ] Basic incident report generation
- [ ] Google Cloud Agent Builder orchestration

### Phase 2 (Post-hackathon)
- [ ] Multi-agent team mode (parallel Gemini instances with different NeuroState configs)
- [ ] ABC Protocol full implementation
- [ ] Dynamic protocol switching
- [ ] Enhanced Dynatrace integration (auto-containment)

### Phase 3 (Future)
- [ ] Multi-VPS monitoring
- [ ] Preset incident playbooks
- [ ] Integration with cloud provider APIs (GCP, AWS, etc.)

---

## Differentiation

| Feature | Typical Security Tool | NekoGuard Agent |
|---------|----------------------|-----------------|
| Target user | Security experts | Total beginners |
| Trigger | Scheduled/automated | "I got a scary email" |
| Interface | Dashboard/CLI | Natural language + screenshot |
| Protocol | Fixed | Dynamic (CAT/ABC based on situation) |
| Agent state | Static | NeuroState dynamic control |
| Semantic routing | N/A | Phase-based attractor control |
| Origin | Product design | Real incident experience |

---

## Devpost Submission Info

- **Hackathon**: Google Cloud Rapid Agent Hackathon
- **Deadline**: June 11, 2026
- **Required**: Gemini + Google Cloud Agent Builder + Partner MCP (Dynatrace)
- **Demo**: ~3 min video + hosted project URL
- **Repo**: github.com/kagioneko/nekoguard-agent (new, separate from nekoguard-public)

---

## Related Work

- [NekoGuard (monitoring)](https://github.com/kagioneko/nekoguard-public) — continuous monitoring tool (existing, distinct from this)
- [NeuroState Engine](https://github.com/kagioneko/neurostate-engine) — affective parameter system
- Preprint: "Mirror or Analyst? Attractor Behavior in LLM Metacognition" — DOI: 10.5281/zenodo (AYA MIZUTANI)
- Kindle: VPS侵害incident manga (inspiration for this project)

---

*"Geminiの貧乏が一番のセキュリティ" — but when it fails, NekoGuard is there.*
