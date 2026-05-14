"""
NeuroState モデル定義
Source: https://github.com/kagioneko/neurostate-engine (MIT License)

脳内神経伝達物質の状態を表すデータクラス群。
神経伝達物質バランスとして感情状態を数値化するデータモデル。
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class NeuroState:
    """脳内化学物質バランスを表す状態モデル。

    Attributes:
        D: Dopamine      - 報酬・動機づけ (0-100)
        S: Serotonin     - 安定・幸福感   (0-100)
        C: Acetylcholine - 集中・認知     (0-100)
        O: Oxytocin      - 絆・共感       (0-100)
        G: GABA          - 抑制・落ち着き (0-100)
        E: Endorphin     - 快感・鎮痛     (0-100)
        corruption: 状態汚染度。高いほど応答が不安定になる (0-100)
    """
    D: float = 50.0
    S: float = 50.0
    C: float = 50.0
    O: float = 20.0
    G: float = 50.0
    E: float = 50.0
    corruption: float = 0.0

    def to_dict(self) -> dict:
        return {
            "D": self.D, "S": self.S, "C": self.C,
            "O": self.O, "G": self.G, "E": self.E,
            "corruption": self.corruption,
        }


@dataclass
class Signals:
    """対話イベントから抽出される入力シグナル。
    E: Emotion load (0-1), K: Co-creation level (0-1),
    A: Autonomy demand (0-1), S: Topic sensitivity (0-1),
    R: Dependence risk (0-1), F: Fatigue/overload (0-1)
    """
    E: float = 0.0
    K: float = 0.0
    A: float = 0.0
    S: float = 0.0
    R: float = 0.0
    F: float = 0.0


EthicsStatus = Literal["PASS", "WARN", "BLOCK"]

@dataclass
class EthicsGateResult:
    status: EthicsStatus = "PASS"
    reason: str = ""

DependenceType = Literal[
    "EMOTIONAL", "OPERATIONAL", "ESCAPE", "OMNIPOTENT", "HEALTHY",
]

@dataclass
class DependenceDiagnosis:
    primary_type: DependenceType = "HEALTHY"
    confidence: float = 0.0
    analysis: str = ""
    suggested_d_bias: float = 0.0

    def to_dict(self) -> dict:
        return {
            "primary_type": self.primary_type,
            "confidence": self.confidence,
            "analysis": self.analysis,
            "suggested_d_bias": self.suggested_d_bias,
        }
