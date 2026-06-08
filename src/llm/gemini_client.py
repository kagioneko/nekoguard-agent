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

        self.model_name = "gemini-3.5-flash"

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
            system_prompt = (
                "You are NekoGuard, an AI security incident response agent. "
                "Analyze incidents calmly, reassure the user, and provide clear action steps. "
                "Always respond in English. Use 'Nya!' occasionally to keep your friendly cat personality."
            )

        # Add English + conciseness instruction to system prompt
        system_prompt += "\n\nIMPORTANT: Always respond in English. After the [NEKOGUARD_NEURO_LOG] header, keep your response to MAXIMUM 3 bullet points or 80 words. Be extremely concise and direct. No lengthy paragraphs."

        # --- User prompt: phase instructions + target data ---
        phase_instructions = {
            1: "[Phase 1: Wide-scan]\nBriefly identify anomalies and affected scope. Stay calm and reassuring. Max 3 bullet points.",
            2: "[Phase 2: Judgment]\nState severity and whether this is Active Breach or Past Breach. List top 2-3 priority actions. Be direct.",
            3: "[Phase 3: Detail Analysis]\nForensic summary: attack vector, breach path, exposed data. Technical, minimal emotion. Max 4 bullet points.",
            4: "[Phase 4: Recovery]\nVerdict: 'Active Breach' or 'Past Breach'. Give the 3 most critical first actions. Brief and actionable.",
        }

        user_prompt = (
            f"[NeuroState] {state}\n\n"
            f"{phase_instructions.get(phase, phase_instructions[1])}\n\n"
            f"[Incident Data]\n"
            f"{input_data if not is_image else 'Image data (screenshot)'}"
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
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                    )
                )
                return {"text": response.text}
            except Exception as e2:
                return {"text": f"Error generating content: {e2}"}
