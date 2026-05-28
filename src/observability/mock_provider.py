"""
MockObservabilityProvider

demo/ ディレクトリの fixture JSON を読み込んで ObservabilitySnapshot を返す。
Dynatrace trial 開始前のデモ・開発用。
"""

import json
import os
from .provider import ObservabilityProvider
from .schema import ObservabilitySnapshot, AlertItem, SuspiciousIp, LogFinding


class MockObservabilityProvider(ObservabilityProvider):
    """
    fixture JSON ベースのモックプロバイダー。
    scenario="active_breach" → dynatrace_active_breach.json
    scenario="past_breach"   → dynatrace_past_breach.json
    """

    def __init__(self, scenario: str = "active_breach"):
        self.scenario = scenario
        self._fixture_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "demo"
        )

    def is_available(self) -> bool:
        return True

    def get_snapshot(self, time_window: str = "last_30m") -> ObservabilitySnapshot:
        filename = f"dynatrace_{self.scenario}.json"
        path = os.path.join(self._fixture_dir, filename)

        if not os.path.exists(path):
            # フォールバック: テキストログをそのまま使う
            return ObservabilitySnapshot(
                source="mock",
                time_window=time_window,
                scenario=self.scenario,
                alerts=[AlertItem(
                    severity="critical",
                    title="Unauthorized access detected (fallback mock)",
                    timestamp="",
                    affected_service="unknown",
                )],
            )

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        alerts = [
            AlertItem(
                severity=a.get("severity", "high"),
                title=a.get("title", ""),
                timestamp=a.get("timestamp", ""),
                affected_service=a.get("affected_service", ""),
                problem_id=a.get("problem_id", ""),
                status=a.get("status", "open"),
            )
            for a in data.get("alerts", [])
        ]

        suspicious_ips = [
            SuspiciousIp(
                ip=ip.get("ip", ""),
                reason=ip.get("reason", ""),
                confidence=ip.get("confidence", 0.0),
                geo=ip.get("geo", ""),
                first_seen=ip.get("first_seen", ""),
                last_seen=ip.get("last_seen", ""),
            )
            for ip in data.get("suspicious_ips", [])
        ]

        log_findings = [
            LogFinding(
                timestamp=f.get("timestamp", ""),
                source=f.get("source", ""),
                summary=f.get("summary", ""),
                risk=f.get("risk", "unknown"),
            )
            for f in data.get("log_findings", [])
        ]

        return ObservabilitySnapshot(
            source="mock",
            time_window=time_window,
            scenario=data.get("scenario", self.scenario),
            alerts=alerts,
            suspicious_ips=suspicious_ips,
            log_findings=log_findings,
            affected_services=data.get("affected_services", []),
        )
