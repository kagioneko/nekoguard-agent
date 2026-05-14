"""
NeuroState 相互作用行列
Source: https://github.com/kagioneko/neurostate-engine (MIT License)

行インデックス: [D, S, C, O, G, E]
MATRIX_A[i][j] = 物質 j が物質 i に与える影響
"""

import math
from typing import List

MATRIX_A: List[List[float]] = [
    [ 0.90, -0.10,  0.10,  0.00, -0.20,  0.10],  # D (Dopamine)
    [-0.10,  0.90, -0.05,  0.00,  0.20, -0.05],  # S (Serotonin)
    [ 0.10,  0.00,  0.95,  0.00,  0.00,  0.10],  # C (Acetylcholine)
    [ 0.00,  0.20,  0.00,  0.90, -0.10,  0.20],  # O (Oxytocin)
    [-0.15,  0.30,  0.00, -0.10,  0.90, -0.20],  # G (GABA)
    [ 0.20, -0.20,  0.10,  0.10, -0.30,  0.90],  # E (Endorphin)
]

EXTERNAL_FORCE_COEFFS: List[float] = [
    1.0,   # D
    0.0,   # S: 外部刺激の影響なし（自律回復）
    0.5,   # C
    0.3,   # O
   -0.4,   # G（興奮すると抑制が下がる）
    0.6,   # E
]

def sigmoid(x: float, k: float = 2.0, m: float = 0.0) -> float:
    return 1.0 / (1.0 + math.exp(-k * (x - m)))

def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(max_val, value))

def matrix_multiply_state(state_vec: List[float]) -> List[float]:
    result = [0.0] * 6
    for i in range(6):
        for j in range(6):
            result[i] += MATRIX_A[i][j] * state_vec[j]
    return result

def apply_external_force(state_vec: List[float], input_power: float) -> List[float]:
    return [
        state_vec[i] + EXTERNAL_FORCE_COEFFS[i] * input_power
        for i in range(6)
    ]
