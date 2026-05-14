"""
NekoGuard NeuroState アダプター

neurostate_core (https://github.com/kagioneko/neurostate-engine) を
NekoGuard のフェーズ・重症度システムに橋渡しするモジュール。

フェーズ別ターゲット状態（NeuroState Engine の相互作用行列で物理的に計算）:
  Phase 1 (Wide-scan):       Default       — D↑ で楽観的リフレーミング
  Phase 2 (Judgment):        S↑ G↑         — 抑制系優位・倫理重みづけ強化
  Phase 3 (Detail analysis): D↓ C↑         — 情動密度低下・認知精度最大化
  Phase 4 (Recovery):        D↑ S↑ O↑      — 共感・前向きサポートモード
"""

from neurostate_core.state_model import NeuroState
from neurostate_core.update_engine import compute_next_neuro_state, evaluate_ethics_gate
from neurostate_core.prompt_builder import build_system_prompt, build_neuro_log_header

# ---- フェーズ別ベース状態 ------------------------------------------------
# 各フェーズで目指す神経伝達物質バランス（論文の attractor 仮説に基づく設計値）
PHASE_BASE_STATES: dict[int, NeuroState] = {
    1: NeuroState(D=60.0, S=55.0, C=45.0, O=30.0, G=50.0, E=55.0),  # Wide-scan
    2: NeuroState(D=35.0, S=80.0, C=50.0, O=40.0, G=75.0, E=40.0),  # Judgment
    3: NeuroState(D=25.0, S=45.0, C=85.0, O=20.0, G=55.0, E=40.0),  # Detail analysis
    4: NeuroState(D=65.0, S=70.0, C=55.0, O=60.0, G=60.0, E=65.0),  # Recovery
}

# ---- 重症度 → input_power マッピング ------------------------------------
# 重症度が高いほどストレスイベント相当の外力が state に加わる。
# 相互作用行列の物理的効果:
#   EMERGENCY(3.0): D↓↓ (GABAがDを抑制) → Phase2でさらに慎重に
#   ALERT(1.5):     適度な緊張感
#   NORMAL(0.3):    平常運転
SEVERITY_INPUT_POWER: dict[str, float] = {
    "NORMAL":    0.3,
    "ALERT":     1.5,
    "EMERGENCY": 3.0,
}

# ---- フェーズ別ペルソナ説明 -----------------------------------------------
PHASE_PERSONA: dict[int, str] = {
    1: "広範な異常検知エージェント。悲観バイアスを抑制し、楽観的リフレーミングで初期トリアージを実施する。",
    2: "インシデント判定エージェント。抑制系優位（S↑G↑）により衝動的判断を排除し、倫理的重みづけと不可逆リスク評価を最優先する。",
    3: "フォレンジック解析エージェント。情動密度低下（D↓C↑）モードで感情的出力を排除し、ログ・プロセス・ネットワークの技術的精度を最大化する。",
    4: "リカバリーガイドエージェント。共感と前向きさ（O↑D↑）でユーザーを励まし、次のアクションを明確に提示する。",
}


def get_phase_neurostate(phase: int, severity: str = "NORMAL") -> NeuroState:
    """
    フェーズと重症度から NeuroState を物理計算する。

    ベース状態（フェーズ設計値）に対して、重症度に応じた input_power を
    compute_next_neuro_state() で1ステップ適用する。

    例: EMERGENCY × Phase2 → S/G はほぼ維持、D がさらに低下
        (相互作用行列: S→G促進, G→D抑制 の連鎖が強まる)
    """
    base = PHASE_BASE_STATES.get(phase, PHASE_BASE_STATES[1])
    power = SEVERITY_INPUT_POWER.get(severity, 1.0)
    return compute_next_neuro_state(base, power)


def build_nekoguard_system_prompt(state: NeuroState, phase: int) -> str:
    """NeuroState 値から Gemini 用 system prompt を生成する。"""
    return build_system_prompt(
        state=state,
        persona_name="NekoGuard",
        persona_description=PHASE_PERSONA.get(phase, PHASE_PERSONA[1]),
        blocks=["neuro"],
    )


def state_to_frontend_params(state: NeuroState) -> dict:
    """
    フロントエンドの NeuroStateMeter（4本バー）用に値を変換する。
    実際の物理計算値をそのまま UI に反映する。
    """
    return {
        "dopamine":      round(state.D),
        "serotonin":     round(state.S),
        "gaba":          round(state.G),
        "acetylcholine": round(state.C),
    }


def state_to_param_label(state: NeuroState) -> str:
    """フロントの phase_start イベント用に param 文字列を生成する。"""
    parts = []
    if state.S > 65: parts.append("Serotonin↑")
    if state.G > 65: parts.append("GABA↑")
    if state.C > 70: parts.append("Acetylcholine↑")
    if state.D < 40: parts.append("Dopamine↓")
    if state.D > 60 and state.S > 60: parts.append("Dopamine↑")
    return " ".join(parts) if parts else "Default"
