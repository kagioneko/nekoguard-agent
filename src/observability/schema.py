"""
NekoGuard 正規化スキーマ

Dynatrace の生レスポンスをこの形式に変換して agent flow に渡す。
Mock / 実 Dynatrace どちらもこのスキーマに揃える。
"""

from dataclasses import dataclass, field


@dataclass
class AlertItem:
    severity: str          # "critical" | "high" | "medium" | "low"
    title: str
    timestamp: str
    affected_service: str
    problem_id: str = ""
    status: str = "open"   # "open" | "resolved"


@dataclass
class SuspiciousIp:
    ip: str
    reason: str
    confidence: float      # 0.0 - 1.0
    geo: str = ""
    first_seen: str = ""
    last_seen: str = ""


@dataclass
class LogFinding:
    timestamp: str
    source: str
    summary: str
    risk: str              # "unauthorized_access" | "credential_exposure" | "malware_execution" | etc.


@dataclass
class ObservabilitySnapshot:
    source: str                          # "dynatrace" | "mock"
    time_window: str                     # "last_30m" | "last_24h"
    scenario: str = ""                   # "active_breach" | "past_breach" | ""
    alerts: list[AlertItem] = field(default_factory=list)
    suspicious_ips: list[SuspiciousIp] = field(default_factory=list)
    log_findings: list[LogFinding] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)

    def to_log_text(self) -> str:
        """agent の analyze_incident() に渡すテキスト形式に変換"""
        lines = [f"[Dynatrace Snapshot] source={self.source} window={self.time_window}"]
        for a in self.alerts:
            status = f" [{a.status.upper()}]" if a.status != "open" else ""
            lines.append(
                f"ALERT [{a.severity.upper()}]{status} {a.title} @ {a.affected_service}"
            )
        for ip in self.suspicious_ips:
            lines.append(
                f"SUSPICIOUS_IP {ip.ip} geo={ip.geo} "
                f"confidence={ip.confidence:.2f} reason={ip.reason}"
            )
        for f in self.log_findings:
            lines.append(
                f"LOG_FINDING [{f.risk}] {f.summary} source={f.source}"
            )
        if self.affected_services:
            lines.append(f"AFFECTED_SERVICES: {', '.join(self.affected_services)}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """API レスポンス用"""
        return {
            "source": self.source,
            "time_window": self.time_window,
            "scenario": self.scenario,
            "alerts": [a.__dict__ for a in self.alerts],
            "suspicious_ips": [ip.__dict__ for ip in self.suspicious_ips],
            "log_findings": [f.__dict__ for f in self.log_findings],
            "affected_services": self.affected_services,
        }
