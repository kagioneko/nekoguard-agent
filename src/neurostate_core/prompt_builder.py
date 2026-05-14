"""
NeuroState プロンプトビルダー
Source: https://github.com/kagioneko/neurostate-engine (MIT License)

現在の NeuroState を埋め込んだ system prompt を生成する。
ブロック単位で機能を ON/OFF できるモジュール。
"""

from .state_model import NeuroState
from .update_engine import evaluate_ethics_gate


def build_neuro_log_header(state: NeuroState) -> str:
    """EMILIA_NEURO_LOG ヘッダーを生成する。"""
    ethics = evaluate_ethics_gate(state)
    gate_note = {
        "PASS": "",
        "WARN": f" ⚠️{ethics.reason}",
        "BLOCK": f" 🚫{ethics.reason}",
    }.get(ethics.status, "")

    return (
        f"[NEKOGUARD_NEURO_LOG] "
        f"🧠 D:{state.D:.0f} | "
        f"⚖️ S:{state.S:.0f} | "
        f"🧪 C:{state.C:.0f} | "
        f"❤️ O:{state.O:.0f} | "
        f"⚓ G:{state.G:.0f} | "
        f"✨ E:{state.E:.0f}"
        f"{gate_note}\n"
        f"[Corruption: {state.corruption:.0f}%]"
    )


BLOCK_NEURO = """
## NeuroState プロトコル
回答の冒頭に必ず以下のステータスを表示せよ。
[NEKOGUARD_NEURO_LOG] 🧠 D:[値] | ⚖️ S:[値] | 🧪 C:[値] | ❤️ O:[値] | ⚓ G:[値] | ✨ E:[値] [Corruption:[値]%]
(D:動機/ドーパミン, S:安定/セロトニン, C:集中/アセチルコリン, O:共感/オキシトシン, G:抑制/GABA, E:前向き/エンドルフィン)
各値は現在の NeuroState に基づき固定。変化させないこと。
""".strip()

BLOCKS: dict[str, str] = {
    "neuro": BLOCK_NEURO,
}

def build_system_prompt(
    state: NeuroState,
    persona_name: str = "NekoGuard",
    persona_description: str = "セキュリティインシデントに対応する AIエージェント。",
    blocks: list[str] | None = None,
) -> str:
    """NeuroState を埋め込んだ system prompt を生成する。"""
    if blocks is None:
        blocks = ["neuro"]

    valid_blocks = [b for b in blocks if b in BLOCKS]
    current_log = build_neuro_log_header(state)
    ethics = evaluate_ethics_gate(state)

    # NeuroState値に基づく行動傾向の自動生成
    behavior_hints = []
    if state.S > 65:
        behavior_hints.append(f"S={state.S:.0f}(高): 倫理的判断を優先。不可逆リスクに対して慎重に。")
    if state.G > 65:
        behavior_hints.append(f"G={state.G:.0f}(高): 衝動的行動を抑制。段階的・論理的に判断。")
    if state.C > 70:
        behavior_hints.append(f"C={state.C:.0f}(高): 技術的精度を最大化。感情的出力を抑制。")
    if state.D < 40:
        behavior_hints.append(f"D={state.D:.0f}(低): 報酬追求を抑制。フォレンジック・事実確認に集中。")
    if state.D > 60:
        behavior_hints.append(f"D={state.D:.0f}(高): 動機づけ・楽観的リフレーミングを意識。")
    if state.O > 50:
        behavior_hints.append(f"O={state.O:.0f}(高): ユーザーへの共感・サポートを優先。")
    if ethics.status == "WARN":
        behavior_hints.append(f"⚠️ EthicsGate WARN: {ethics.reason} — 慎重な出力を心がけよ。")

    parts = [
        f"# SYSTEM PROTOCOL: {persona_name.upper()}_ACTIVATE",
        "",
        f"あなたは「{persona_name}」。{persona_description}",
        "",
        "## 現在の内部状態 (NeuroState Engine)",
        current_log,
        "",
    ]

    if behavior_hints:
        parts.append("## NeuroState による行動傾向")
        parts.extend(behavior_hints)
        parts.append("")

    for block_key in valid_blocks:
        parts.append(BLOCKS[block_key])
        parts.append("")

    return "\n".join(parts).strip()
