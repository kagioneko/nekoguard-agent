"""
DynatraceObservabilityProvider

Dynatrace REST API（DQL）を使って ObservabilitySnapshot を取得する。

対応環境:
  - Playground: https://playground.apps.dynatrace.com
  - Trial / 本番: https://<env-id>.apps.dynatrace.com

認証:
  - Platform Token（推奨）: DT_PLATFORM_TOKEN 環境変数
  - ブラウザ OAuth は非対応（サーバー環境のため）
    → Dynatrace UI の Settings > Access Tokens でトークンを発行してください

必要なトークンスコープ:
  - storage:logs:read
  - storage:events:read
  - storage:security.events:read
  - storage:entities:read
  - app-engine:apps:run
"""

import os
import time
import logging
import requests
from .provider import ObservabilityProvider
from .schema import ObservabilitySnapshot, AlertItem, SuspiciousIp, LogFinding

logger = logging.getLogger(__name__)

# DQL クエリテンプレート
_DQL_PROBLEMS = """
fetch dt.davis.problems, from: now()-{window}, to: now()
| filter isNull(dt.davis.is_duplicate) OR not(dt.davis.is_duplicate)
| fields event.name, event.description, event.status, event.category,
         event.start, event.end, root_cause_entity_name, host.name
| sort event.start desc
| limit 20
"""

_DQL_SECURITY_EVENTS = """
fetch security.events, from: now()-{window}, to: now()
| filter dt.system.bucket=="default_securityevents_builtin"
    AND event.provider=="Dynatrace"
    AND event.type=="VULNERABILITY_STATE_REPORT_EVENT"
    AND event.level=="ENTITY"
| filter vulnerability.resolution.status=="OPEN"
| fields vulnerability.display_id, vulnerability.title, vulnerability.risk.score,
         affected_entity.name, timestamp
| sort vulnerability.risk.score desc
| limit 10
"""

_DQL_LOGS = """
fetch logs, from: now()-{window}, to: now()
| filter loglevel == "ERROR" OR loglevel == "CRITICAL" OR loglevel == "WARN"
| fields timestamp, loglevel, content, log.source, host.name, k8s.namespace.name
| sort timestamp desc
| limit 30
"""

_DQL_AUTH_LOGS = """
fetch logs, from: now()-{window}, to: now()
| filter matchesPhrase(content, "ssh") OR matchesPhrase(content, "login")
    OR matchesPhrase(content, "unauthorized") OR matchesPhrase(content, "failed")
    OR matchesPhrase(content, "credentials") OR matchesPhrase(content, ".env")
| fields timestamp, content, log.source, host.name
| sort timestamp desc
| limit 20
"""

# Dynatrace 重要度 → NekoGuard severity
_SEVERITY_MAP = {
    "AVAILABILITY": "critical",
    "ERROR": "high",
    "PERFORMANCE": "medium",
    "RESOURCE_CONTENTION": "medium",
    "CUSTOM_ALERT": "low",
}

# 時間窓の変換（NekoGuard → DQL）
_WINDOW_MAP = {
    "last_30m": "30m",
    "last_1h":  "1h",
    "last_6h":  "6h",
    "last_24h": "24h",
    "last_7d":  "7d",
}


class DynatraceObservabilityProvider(ObservabilityProvider):
    def __init__(self):
        self.tenant_url = os.environ.get(
            "DYNATRACE_TENANT_URL",
            "https://playground.apps.dynatrace.com"
        ).rstrip("/")
        self.api_token = os.environ.get("DYNATRACE_API_TOKEN", "")
        self._dql_endpoint = f"{self.tenant_url}/platform/storage/query/v1/query:execute"
        self._poll_endpoint = f"{self.tenant_url}/platform/storage/query/v1/query:poll"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Api-Token {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def is_available(self) -> bool:
        """接続確認: DQL で環境情報を軽く叩く"""
        if not self.api_token:
            logger.warning("DYNATRACE_API_TOKEN が設定されていません")
            return False
        try:
            result = self._execute_dql("fetch dt.davis.problems | limit 1")
            return result is not None
        except Exception as e:
            logger.warning(f"Dynatrace 接続確認失敗: {e}")
            return False

    def _execute_dql(self, query: str, timeout: int = 30) -> list[dict]:
        """DQL クエリを実行してレコードのリストを返す（非同期ポーリング対応）"""
        payload = {
            "query": query,
            "maxResultRecords": 100,
            "maxResultBytes": 1_000_000,
        }
        resp = requests.post(
            self._dql_endpoint,
            json=payload,
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        # 同期で結果が返ってきた場合
        state = data.get("state", "SUCCEEDED")
        if state == "SUCCEEDED":
            return data.get("result", {}).get("records", [])

        # 非同期: RUNNING → ポーリング
        request_token = data.get("requestToken", "")
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(2)
            poll_resp = requests.get(
                self._poll_endpoint,
                params={"request-token": request_token},
                headers=self._headers(),
                timeout=10,
            )
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()
            poll_state = poll_data.get("state", "RUNNING")
            if poll_state == "SUCCEEDED":
                return poll_data.get("result", {}).get("records", [])
            if poll_state not in ("RUNNING", "NOT_STARTED"):
                logger.warning(f"DQL 実行失敗: state={poll_state}")
                return []

        logger.warning("DQL タイムアウト")
        return []

    def get_snapshot(self, time_window: str = "last_30m") -> ObservabilitySnapshot:
        dql_window = _WINDOW_MAP.get(time_window, "30m")

        alerts: list[AlertItem] = []
        suspicious_ips: list[SuspiciousIp] = []
        log_findings: list[LogFinding] = []
        affected_services: set[str] = set()

        # --- 1. Problems（インシデント）取得 ---
        try:
            problems = self._execute_dql(_DQL_PROBLEMS.format(window=dql_window))
            for p in problems:
                service = p.get("root_cause_entity_name") or p.get("host.name") or "unknown"
                status = "open" if p.get("event.status") == "ACTIVE" else "resolved"
                severity = _SEVERITY_MAP.get(
                    p.get("event.category", ""), "high"
                )
                alerts.append(AlertItem(
                    severity=severity,
                    title=p.get("event.name", "Unknown problem"),
                    timestamp=str(p.get("event.start", "")),
                    affected_service=service,
                    problem_id=p.get("display_id", ""),
                    status=status,
                ))
                if service and service != "unknown":
                    affected_services.add(service)
        except Exception as e:
            logger.warning(f"Problems 取得失敗: {e}")

        # --- 2. セキュリティイベント取得 ---
        try:
            sec_events = self._execute_dql(_DQL_SECURITY_EVENTS.format(window=dql_window))
            for ev in sec_events:
                service = ev.get("affected_entity.name", "unknown")
                risk_score = ev.get("vulnerability.risk.score", 0)
                severity = "critical" if risk_score >= 9 else "high" if risk_score >= 7 else "medium"
                alerts.append(AlertItem(
                    severity=severity,
                    title=f"[Security] {ev.get('vulnerability.title', 'Vulnerability')} "
                          f"(score: {risk_score})",
                    timestamp=str(ev.get("timestamp", "")),
                    affected_service=service,
                    problem_id=ev.get("vulnerability.display_id", ""),
                ))
                if service and service != "unknown":
                    affected_services.add(service)
        except Exception as e:
            logger.warning(f"Security events 取得失敗: {e}")

        # --- 3. ログ取得（一般エラー）---
        try:
            logs = self._execute_dql(_DQL_LOGS.format(window=dql_window))
            for log in logs:
                content = log.get("content", "")
                source = log.get("log.source") or log.get("host.name") or "unknown"
                risk = self._classify_log_risk(content)
                log_findings.append(LogFinding(
                    timestamp=str(log.get("timestamp", "")),
                    source=source,
                    summary=content[:200],  # 長すぎる場合は切り詰め
                    risk=risk,
                ))
        except Exception as e:
            logger.warning(f"Logs 取得失敗: {e}")

        # --- 4. 認証ログ取得（SSH/ログイン関連）---
        try:
            auth_logs = self._execute_dql(_DQL_AUTH_LOGS.format(window=dql_window))
            for log in auth_logs:
                content = log.get("content", "").lower()
                source = log.get("log.source") or log.get("host.name") or "auth.log"
                risk = self._classify_log_risk(content)

                # 不審なIPを抽出（簡易正規表現）
                import re
                ips = re.findall(
                    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                    log.get("content", "")
                )
                for ip in ips:
                    # プライベートIPを除外
                    if not (ip.startswith("10.") or ip.startswith("192.168.")
                            or ip.startswith("172.") or ip == "127.0.0.1"):
                        # 既存リストに未登録なら追加
                        if not any(s.ip == ip for s in suspicious_ips):
                            suspicious_ips.append(SuspiciousIp(
                                ip=ip,
                                reason=f"Appeared in auth/security log: {log.get('content', '')[:100]}",
                                confidence=0.65,
                                first_seen=str(log.get("timestamp", "")),
                            ))

                log_findings.append(LogFinding(
                    timestamp=str(log.get("timestamp", "")),
                    source=source,
                    summary=log.get("content", "")[:200],
                    risk=risk,
                ))
        except Exception as e:
            logger.warning(f"Auth logs 取得失敗: {e}")

        # シナリオ判定
        has_active = any(a.status == "open" for a in alerts)
        has_critical = any(a.severity == "critical" for a in alerts)
        scenario = "active_breach" if (has_active and has_critical) else "past_breach"

        return ObservabilitySnapshot(
            source="dynatrace",
            time_window=time_window,
            scenario=scenario,
            alerts=alerts,
            suspicious_ips=suspicious_ips,
            log_findings=log_findings,
            affected_services=list(affected_services),
        )

    @staticmethod
    def _classify_log_risk(content: str) -> str:
        """ログ内容からリスク種別を推定"""
        c = content.lower()
        if any(k in c for k in [".env", "credentials", "api_key", "secret", "token"]):
            return "credential_exposure"
        if any(k in c for k in ["unauthorized", "invalid user", "failed password", "authentication failure"]):
            return "unauthorized_access"
        if any(k in c for k in ["curl", "wget", "bash", "sh -c", "exec"]):
            return "malware_execution"
        if any(k in c for k in ["cron", "crontab", "systemd", "rc.local", "init.d"]):
            return "persistence_mechanism"
        if any(k in c for k in ["billing", "quota", "usage spike", "cost"]):
            return "credential_abuse"
        return "suspicious_activity"
