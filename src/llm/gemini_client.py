import os
import sys

from google import genai
from google.genai import types

# src ディレクトリをパスに追加（neurostate_adapter のため）
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from neurostate_adapter import build_nekoguard_system_prompt
from neurostate_core.state_model import NeuroState


class GeminiClient:
    def __init__(self):
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "nekoguard-agent")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

        if "GEMINI_API_KEY" in os.environ:
            self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        else:
            self.client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location
            )

        self.model_name = "gemini-2.5-flash"

    def analyze_incident(
        self,
        input_data: str,
        is_image: bool = False,
        state: str = "NORMAL",
        phase: int = 1,
        neuro_state: NeuroState | None = None,
    ) -> dict:
        """
        Gemini API を用いてインシデントログまたは画像を解析する。

        neuro_state が渡された場合、NeuroState Engine の build_system_prompt() で
        生成した system_instruction を Gemini に注入する（アトラクター誘導）。
        """

        # --- System prompt: NeuroState Engine 経由で生成 ---
        if neuro_state is not None:
            system_prompt = build_nekoguard_system_prompt(neuro_state, phase)
        else:
            # フォールバック（neuro_state 未渡しの場合）
            system_prompt = (
                "あなたはセキュリティ対応 AI エージェント「NekoGuard」です。"
                "インシデントを冷静に分析し、ユーザーを安心させながら対応策を提示してください。"
            )

        # --- User prompt: フェーズ指示 + 解析対象 ---
        phase_instructions = {
            1: "【Phase 1: Wide-scan】\n広範な異常検知を行い、影響サービス・範囲を特定してください。初期トリアージとして楽観的にリフレーミングし、パニックを防ぐ表現を心がけてください。",
            2: "【Phase 2: Judgment】\n侵害の深刻度・緊急度を評価し、Active Breach か Past Breach かを判断してください。不可逆操作リスクを最重視し、段階的なアクション優先度を示してください。",
            3: "【Phase 3: Detail analysis】\nログ・プロセス・ネットワークのフォレンジック解析を行い、攻撃手法・侵害経路・漏洩可能性を技術的に詳述してください。感情的表現は最小限に。",
            4: "【Phase 4: Recovery】\n分析を統合し、最終判断として「Active Breach」か「Past Breach」かを明示してください。ユーザーが最初の5分で取るべき行動を、優しく・具体的に提示してください。",
        }

        user_prompt = (
            f"【NeuroState】{state}\n\n"
            f"{phase_instructions.get(phase, phase_instructions[1])}\n\n"
            f"【解析対象情報】\n"
            f"{input_data if not is_image else '画像データ（スクリーンショット）'}"
        )

        contents: list = [user_prompt]
        if is_image:
            with open(input_data, "rb") as f:
                image_data = f.read()
            contents.append(
                types.Part.from_bytes(
                    data=image_data,
                    mime_type="image/png"
                )
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                )
            )
            return {"text": response.text}
        except Exception as e:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                    )
                )
                return {"text": response.text}
            except Exception as e2:
                return {"text": f"Error generating content: {e2}"}
