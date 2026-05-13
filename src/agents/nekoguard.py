# NekoGuard Agent - Main
import os
import sys
import argparse

# Windows cp932 環境での絵文字出力対応ニャン 🐱
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

# src ディレクトリを Python パスに追加
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from llm.gemini_client import GeminiClient
from llm.gemini_mock import GeminiMock

class NekoGuardAgent:
    def __init__(self, demo_mode=False):
        self.neurostate = "NORMAL"
        self.demo_mode = demo_mode
        if demo_mode:
            print("🐱 起動モード: DEMO (Mock Gemini & Mock Logs)")
            self.llm = GeminiMock()
        else:
            print("🐱 起動モード: REAL (Gemini 3 API & Real Logs)")
            self.llm = GeminiClient()
            
    def detect_keywords(self, text: str) -> str:
        """キーワードからNeuroStateレベル判定"""
        emergency_keywords = [
            "ポリシー違反", "乗っ取り", "停止", "不正行為",
            "ssh key", "private key", "credentials leaked",
            "root", "unauthorized", "critical", "不正アクセス", "漏洩"
        ]
        alert_keywords = [
            "早急に対応", "suspicious", "failed login",
            "permission denied", "billing alert", "warn"
        ]
        
        text_lower = text.lower()
        for keyword in emergency_keywords:
            if keyword in text_lower:
                return "EMERGENCY"
        for keyword in alert_keywords:
            if keyword in text_lower:
                return "ALERT"
        return "NORMAL"
    
    def get_phase_neurostate(self, phase: int) -> dict:
        """各フェーズのNeuroStateパラメーター（モック）"""
        states = {
            1: {"name": "Wide-scan", "param": "Default", "desc": "広範な異常検知、楽観的リフレーミング"},
            2: {"name": "Judgment", "param": "Serotonin↑ GABA↑", "desc": "慎重・倫理的判断、Claude風"},
            3: {"name": "Detail analysis", "param": "Dopamine↓ Acetylcholine↑", "desc": "技術的フォレンジック、Codex風"},
            4: {"name": "Recovery", "param": "Default", "desc": "ユーザーへのガイダンス、励まし"}
        }
        return states.get(phase, states[1])
        
    def determine_breach_status(self, text: str) -> str:
        """テキストから侵害が現在進行形か過去のものかを判定"""
        text_lower = text.lower()
        if "ongoing" in text_lower or "現在進行形" in text_lower or "active" in text_lower or "止まらない" in text_lower:
            return "active"
        if "past" in text_lower or "過去" in text_lower or "already happened" in text_lower:
            return "past"
        # デフォルトは最悪を想定して active
        return "active"
    
    def run(self, input_path: str = None, is_image: bool = False):
        """メインフロー (Multi-Step Planning with NeuroState)"""
        print("\n🐱 NekoGuard起動！データ取得中...")
        
        input_data = ""
        if is_image and input_path:
            input_data = input_path
            print(f"   👉 画像ファイルを解析します: {input_path}")
        elif input_path:
            with open(input_path, 'r', encoding='utf-8') as f:
                input_data = f.read()
            print(f"   👉 ログファイルを読み込みました: {input_path}")
        else:
            # フォールバック
            input_data = "Alert: Unauthorized access detected."

        # 初期状態判定
        if not is_image:
            self.neurostate = self.detect_keywords(input_data)
        
        print(f"⚡ 初期NeuroState: {self.neurostate}\n")
        
        # 4つのフェーズをループ処理 (NeuroState制御)
        print("🧠 [NeuroState Engine] 分析フェーズを開始します...")
        final_plan = ""
        
        for phase in range(1, 5):
            ns = self.get_phase_neurostate(phase)
            print(f"\n--- Phase {phase}: {ns['name']} ({ns['desc']}) ---")
            print(f"   💉 注入パラメーター: {ns['param']}")
            
            # Geminiに状態を渡して分析
            state_context = f"{self.neurostate} | Mode: {ns['name']} | Params: {ns['param']}"
            result = self.llm.analyze_incident(input_data, is_image=is_image, state=state_context, phase=phase)
            print(f"   🤖 思考出力:\n{result['text']}\n")
            
            if phase == 4:
                final_plan = result['text']
                
        # 最終判断からBreach Statusを判定
        breach_status = self.determine_breach_status(final_plan)

        # 実行フェーズ
        if self.neurostate in ["EMERGENCY", "ALERT"]:
            print("\n🚨 NekoGuard: 分析が完了したニャ。プロトコルへ移行するよ。")
            print("   まずは深呼吸してニャ。ボクがしっかりサポートするから大丈夫だよ。")
            user_input = input("❓ 提案された対応計画を実行しますか？ (Y/n): ")
            if user_input.strip().lower() in ['y', 'yes', '']:
                from protocols.incident_protocol import IncidentResponseProtocol
                protocol = IncidentResponseProtocol(demo_mode=self.demo_mode)
                protocol.execute(breach_status=breach_status)
            else:
                print("⛔ 対応計画の実行をキャンセルしましたニャ。")
        else:
            print("✅ 正常稼働中です。対応は不要です。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NekoGuard Agent")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with mock data")
    parser.add_argument("--real", action="store_true", help="Run in real mode with API")
    args = parser.parse_args()
    
    demo_mode = args.demo or not args.real
    agent = NekoGuardAgent(demo_mode=demo_mode)
    
    print("\n===============================")
    print("🐾 NekoGuard Agent CLI")
    print("===============================")
    
    user_input = input("👉 解析するログ、または画像のパスを入力してニャ (Enterでデフォルトdemo/sample_alert.logを使用): ")
    
    input_path = user_input.strip()
    is_image = False
    
    if not input_path:
        input_path = os.path.join(PROJECT_ROOT, "demo", "sample_alert.log")
        print(f"   (デフォルトを使用します: {input_path})")
    
    if input_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        is_image = True
        
    if os.path.exists(input_path):
        agent.run(input_path, is_image=is_image)
    else:
        print(f"❌ エラー: ファイルが見つからないニャ ({input_path})")