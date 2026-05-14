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
from neurostate_adapter import (
    get_phase_neurostate,
    state_to_frontend_params,
    state_to_param_label,
)
from neurostate_core.prompt_builder import build_neuro_log_header


class NekoGuardAgent:
    def __init__(self, demo_mode=False):
        self.neurostate = "NORMAL"
        self.demo_mode = demo_mode
        if demo_mode:
            print("🐱 起動モード: DEMO (Mock Gemini & Mock Logs)")
            self.llm = GeminiMock()
        else:
            print("🐱 起動モード: REAL (Gemini API & Real Logs)")
            self.llm = GeminiClient()

    def detect_keywords(self, text: str) -> str:
        """キーワードから NeuroState レベル判定"""
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
        """
        各フェーズの NeuroState を計算して返す。
        NeuroState Engine の相互作用行列で物理計算した実値を使用。
        """
        ns = get_phase_neurostate(phase, self.neurostate)
        frontend_params = state_to_frontend_params(ns)
        param_label = state_to_param_label(ns)

        phase_meta = {
            1: {"name": "Wide-scan",      "desc": "広範な異常検知、楽観的リフレーミング"},
            2: {"name": "Judgment",       "desc": "抑制系優位・不可逆リスク評価モード"},
            3: {"name": "Detail analysis","desc": "情動密度低下・技術的精度最大化モード"},
            4: {"name": "Recovery",       "desc": "ユーザーへのガイダンス、励まし"},
        }
        meta = phase_meta.get(phase, phase_meta[1])

        return {
            "name":             meta["name"],
            "param":            param_label,
            "desc":             meta["desc"],
            "neuro_state":      ns,          # NeuroState オブジェクト（Gemini注入用）
            "frontend_params":  frontend_params,  # フロントエンド表示用
            "neuro_log":        build_neuro_log_header(ns),  # ログ表示用
        }

    def determine_breach_status(self, text: str) -> str:
        """テキストから侵害が現在進行形か過去のものかを判定"""
        text_lower = text.lower()
        if "ongoing" in text_lower or "現在進行形" in text_lower or "active" in text_lower or "止まらない" in text_lower:
            return "active"
        if "past" in text_lower or "過去" in text_lower or "already happened" in text_lower:
            return "past"
        return "active"  # デフォルトは最悪を想定

    def run(self, input_path: str = None, is_image: bool = False):
        """メインフロー (Multi-Step Planning with NeuroState Engine)"""
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
            input_data = "Alert: Unauthorized access detected."

        if not is_image:
            self.neurostate = self.detect_keywords(input_data)

        print(f"⚡ 初期NeuroState: {self.neurostate}\n")

        print("🧠 [NeuroState Engine] 分析フェーズを開始します...")
        final_plan = ""

        for phase in range(1, 5):
            ns_data = self.get_phase_neurostate(phase)
            print(f"\n--- Phase {phase}: {ns_data['name']} ({ns_data['desc']}) ---")
            print(f"   {ns_data['neuro_log']}")

            state_context = f"{self.neurostate} | Mode: {ns_data['name']} | Params: {ns_data['param']}"
            result = self.llm.analyze_incident(
                input_data,
                is_image=is_image,
                state=state_context,
                phase=phase,
                neuro_state=ns_data["neuro_state"],
            )
            print(f"   🤖 思考出力:\n{result['text']}\n")

            if phase == 4:
                final_plan = result['text']

        breach_status = self.determine_breach_status(final_plan)

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
