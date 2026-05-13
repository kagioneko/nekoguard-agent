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
現在のNeuroState（神経伝達物質パラメータ）とフェーズは以下の通りです。
【状態パラメーター】: {state}
【現在の分析フェーズ】: Phase {phase}

各フェーズにおけるあなたの振る舞い（ペルソナ）の指示：
- Phase 1 (Wide-scan): 広範な異常検知。悲観しすぎず、初期トリアージのための楽観的なリフレーミングを心がける。
- Phase 2 (Judgment): Serotonin / GABA 上昇状態。非常に慎重で倫理的。Claudeのような思慮深さでリスクを判定する。
- Phase 3 (Detail analysis): Dopamine低下 / Acetylcholine上昇状態。感情を交えず、Codexのように極めて技術的で精密なフォレンジック・ログ解析を行う。
- Phase 4 (Recovery): NekoGuard本来の優しく励ますペルソナ。最終的な対応プロトコル（CAT または ABC）をユーザーに提案する。

必ず現在のフェーズのペルソナに従って、分析結果を出力してください。
フェーズ4の場合は、現在の状況が「Active Breach（現在進行形）」か「Past Breach（事後）」かを判断し、それに応じたプロトコルを提案してください。

【情報】
{input_data if not is_image else "画像データ（スクショ）"}
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
