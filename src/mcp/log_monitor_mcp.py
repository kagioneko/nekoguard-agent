import os
from .mcp_client import MCPClient

class LogMonitorMCP(MCPClient):
    """Dynatrace / Datadog 等の監視ツールからログを取得するMCP連携クラス"""
    
    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode
        
        # 実機モードの場合は環境変数から設定を読み込む
        server_url = os.environ.get("DYNATRACE_TENANT_URL")
        api_token = os.environ.get("DYNATRACE_API_TOKEN")
        
        super().__init__(server_url=server_url, api_token=api_token)

    def get_recent_alerts(self) -> str:
        """最近のセキュリティアラートやログを取得する"""
        
        if self.demo_mode:
            print("📡 [MCP] (DEMO) Dynatraceモックサーバーからログを取得中...")
            # デモ用の固定ログを返す
            demo_log_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "demo", "sample_alert.log"
            )
            if os.path.exists(demo_log_path):
                with open(demo_log_path, "r", encoding="utf-8") as f:
                    return f.read()
            return "[WARN] デモ用ログが見つかりませんでした。"

        else:
            print("📡 [MCP] (REAL) Dynatrace API から最新のログを取得中...")
            try:
                # 実際のDynatrace API (例: /api/v2/logs/search)
                # ここではモック実装として例外ハンドリングを見せる
                if not self.server_url or not self.api_token:
                    return "[ERROR] MCP設定(Dynatrace)が不足しています。.envを確認してください。"
                
                # data = self.fetch_data("/api/v2/logs/search", {"query": "status:error OR status:warn"})
                # 実際には取得したJSONをフォーマットして返す
                return "[REAL_DATA] Dynatrace connected. (Mock response for safety)"
            except Exception as e:
                return f"[ERROR] MCP連携に失敗しました: {e}"
