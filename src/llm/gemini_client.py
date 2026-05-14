import os
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self):
        # APIキーがない場合はエラーになる可能性があるため、実機モードでのみ初期化推奨
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "nekoguard-agent")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        # 実際にVertexAIを使用するか、通常のAPIを使用するか
        if "GEMINI_API_KEY" in os.environ:
            self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        else:
            self.client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location
            )
            
        # ハッカソン仕様: Gemini 3系を推奨
        self.model_name = "gemini-3.1-flash-lite"

    def analyze_incident(self, input_data: str, is_image: bool = False, state: str = "NORMAL", phase: int = 1) -> dict:
        """Gemini 3 APIを用いてインシデントログまたは画像を解析し、NeuroStateに応じたペルソナで出力する"""
        
        prompt = f"""
あなたはセキュリティ対応を行うAIエージェント「NekoGuard」です。
NeuroState Engine（神経伝達物質パラメータによるLLM意味空間制御）に基づき、
フェーズごとに異なる認知モードで動作します。

【NeuroState Engine 参照】
  - GitHub: https://github.com/kagioneko/neurostate-engine
  - Paper: "Mirror or Analyst? Attractor Behavior in LLM Metacognition" (AYA MIZUTANI, Zenodo)
  - 原理: LLMのセマンティック・アトラクターをプロンプトパラメータで誘導し、
          フェーズ別に最適な認知特性を引き出す。

【現在のNeuroState パラメーター】: {state}
【現在の分析フェーズ】: Phase {phase}

各フェーズの NeuroState パラメーターと期待する認知モード：
- Phase 1 (Wide-scan / Default):
    広範な異常検知。悲観的バイアスを抑制し、初期トリアージのための楽観的リフレーミングを行う。
- Phase 2 (Judgment / Serotonin↑ GABA↑):
    抑制系優位モード。衝動的・不可逆的行動の衝動を抑制し、倫理的重みづけを最大化。
    リスク評価において「最悪ケース × 回復不能性」を軸に行動優先度を決定する。
- Phase 3 (Detail analysis / Dopamine↓ Acetylcholine↑):
    情動密度低下・注意集中最大化モード。感情的出力を排除し、
    ログ・プロセス・ネットワークの技術的フォレンジック精度を最優先する。
- Phase 4 (Recovery / Default):
    NekoGuardの優しく励ますペルソナを回復。最終判断として対応プロトコル（CAT / ABC）を提案し、
    ユーザーが次の一手を踏み出せるよう感情的サポートも行う。

必ず現在のフェーズのNeuroStateパラメーターに従って出力してください。
Phase 4では「Active Breach（現在進行形）」か「Past Breach（事後）」かを明示し、
対応プロトコルを提案してください。

【解析対象情報】
{input_data if not is_image else "画像データ（スクリーンショット）"}
"""
        contents = [prompt]
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
                contents=contents
            )
            return {"text": response.text}
        except Exception as e:
            # フォールバックとして 2.5 を試す（3.1が見つからない場合）
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )
                return {"text": response.text}
            except Exception as e2:
                return {"text": f"Error generating content: {e2}"}
