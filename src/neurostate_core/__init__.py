"""
NeuroState Engine - コアモジュール
Source: https://github.com/kagioneko/neurostate-engine (MIT License)
Paper: "Mirror or Analyst? Attractor Behavior in LLM Metacognition" (AYA MIZUTANI, Zenodo)
"""

from .state_model import (
    NeuroState,
    Signals,
    EthicsGateResult,
    DependenceDiagnosis,
)
from .update_engine import (
    compute_next_neuro_state,
    evaluate_ethics_gate,
    diagnose_dependence,
    event_to_power,
)
from .interaction_matrix import MATRIX_A, sigmoid, clamp
from .prompt_builder import build_neuro_log_header, build_system_prompt

__all__ = [
    "NeuroState",
    "Signals",
    "EthicsGateResult",
    "DependenceDiagnosis",
    "compute_next_neuro_state",
    "evaluate_ethics_gate",
    "diagnose_dependence",
    "event_to_power",
    "MATRIX_A",
    "sigmoid",
    "clamp",
    "build_neuro_log_header",
    "build_system_prompt",
]
