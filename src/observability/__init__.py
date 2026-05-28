"""
NekoGuard Observability Layer

抽象化された観測データプロバイダー。
MockProvider（fixture JSON）と DynatraceProvider（REST API）を透過的に切り替え可能。
"""

from .provider import ObservabilityProvider
from .schema import ObservabilitySnapshot, AlertItem, SuspiciousIp, LogFinding
from .mock_provider import MockObservabilityProvider

__all__ = [
    "ObservabilityProvider",
    "ObservabilitySnapshot",
    "AlertItem",
    "SuspiciousIp",
    "LogFinding",
    "MockObservabilityProvider",
]
