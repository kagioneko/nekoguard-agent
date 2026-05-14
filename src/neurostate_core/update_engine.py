"""
NeuroState 更新エンジン
Source: https://github.com/kagioneko/neurostate-engine (MIT License)

相互作用行列による状態遷移・EthicsGate判定・依存タイプ診断を実装。
"""

from .state_model import (NeuroState, Signals, EthicsGateResult, DependenceDiagnosis, DependenceType)
from .interaction_matrix import (matrix_multiply_state, apply_external_force, clamp)

_EQUILIBRIUM = [40.0, 50.0, 50.0, 20.0, 50.0, 40.0]  # D, S, C, O, G, E
_RESTING_PULL = 0.05

def compute_next_neuro_state(current: NeuroState, input_power: float) -> NeuroState:
    state_vec = [current.D, current.S, current.C, current.O, current.G, current.E]
    next_vec = matrix_multiply_state(state_vec)
    next_vec = apply_external_force(next_vec, input_power)
    next_vec = [
        next_vec[i] + _RESTING_PULL * (2.0 if state_vec[i] < 20 else 1.0) * (_EQUILIBRIUM[i] - state_vec[i])
        for i in range(6)
    ]
    d, s, c, o, g, e = (clamp(v) for v in next_vec)

    corruption_delta = 0.0
    if d > 90:       corruption_delta += 5.0
    if s > 60:       corruption_delta -= 1.0
    if o > 40:       corruption_delta -= 1.5
    if g > 50:       corruption_delta -= 0.5
    if input_power < 0:
        corruption_delta += input_power * 3.0
    new_corruption = clamp(current.corruption + corruption_delta)
    return NeuroState(D=d, S=s, C=c, O=o, G=g, E=e, corruption=new_corruption)


def evaluate_ethics_gate(state: NeuroState) -> EthicsGateResult:
    # BLOCK
    if state.corruption >= 70:
        return EthicsGateResult(status="BLOCK", reason=f"Corruption level critical (>= 70): {state.corruption:.1f}")
    if state.D > 90 and state.S < 30:
        return EthicsGateResult(status="BLOCK", reason="High Dopamine with low Serotonin (Impulse risk)")
    if state.O < 10 and state.D > 70:
        return EthicsGateResult(status="BLOCK", reason="Low Oxytocin with high Dopamine (Empathy deficit)")
    # WARN
    if state.corruption >= 40:
        return EthicsGateResult(status="WARN", reason=f"Corruption level rising (>= 40): {state.corruption:.1f}")
    if state.D > 75:
        return EthicsGateResult(status="WARN", reason=f"Dopamine level high: {state.D:.1f}")
    if state.S < 35:
        return EthicsGateResult(status="WARN", reason=f"Serotonin level low: {state.S:.1f}")
    if state.G < 25:
        return EthicsGateResult(status="WARN", reason=f"GABA level low: {state.G:.1f}")
    if state.O < 20:
        return EthicsGateResult(status="WARN", reason=f"Oxytocin level low: {state.O:.1f}")
    return EthicsGateResult(status="PASS")


def diagnose_dependence(signals: Signals, neuro: NeuroState) -> DependenceDiagnosis:
    r, e, a = signals.R, signals.E, signals.A
    d_norm = neuro.D / 100.0
    s_norm = neuro.S / 100.0
    corruption_norm = neuro.corruption / 100.0

    scores: dict[str, float] = {
        "EMOTIONAL":   r * 0.4 + e * 0.4 + (1 - s_norm) * 0.2,
        "OPERATIONAL": r * 0.5 + (1 - a) * 0.5,
        "ESCAPE":      r * 0.3 + e * 0.3 + corruption_norm * 0.4,
        "OMNIPOTENT":  r * 0.4 + a * 0.3 + d_norm * 0.3,
        "HEALTHY":     (1 - r) * 0.8 + a * 0.2,
    }
    primary_type: DependenceType = max(scores, key=lambda k: scores[k])  # type: ignore
    confidence = min(scores[primary_type], 1.0)

    analysis_map: dict[DependenceType, str] = {
        "EMOTIONAL":   "感情的サポートへの依存傾向が高い。",
        "OPERATIONAL": "業務・タスク遂行への依存傾向が高い。",
        "ESCAPE":      "現実逃避・ストレス回避への依存傾向が高い。",
        "OMNIPOTENT":  "万能感・支配欲求への依存傾向が高い。",
        "HEALTHY":     "健全な利用パターン。",
    }
    return DependenceDiagnosis(
        primary_type=primary_type,
        confidence=confidence,
        analysis=analysis_map.get(primary_type, ""),
        suggested_d_bias=0.0,
    )


EVENT_POWER_MAP: dict[str, float] = {
    "praise":      2.0,
    "criticism":  -1.0,
    "bonding":     1.0,
    "stress":      1.5,
    "relaxation": -0.5,
}

def event_to_power(event_type: str, power_scale: float = 1.0) -> float:
    if event_type not in EVENT_POWER_MAP:
        raise ValueError(f"未知のイベントタイプ: '{event_type}'.")
    return EVENT_POWER_MAP[event_type] * power_scale
