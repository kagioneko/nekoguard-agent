import os
import requests

class MCPClient:
    """Base client for Model Context Protocol (MCP) integrations."""
    
    def __init__(self, server_url: str = None, api_token: str = None):
        self.server_url = server_url
        self.api_token = api_token
        
    def get_headers(self) -> dict:
        if not self.api_token:
            return {}
        return {
            "Authorization": f"Api-Token {self.api_token}",
            "Content-Type": "application/json"
        }

    def fetch_data(self, endpoint: str, params: dict = None) -> dict:
        if not self.server_url:
            raise ValueError("MCP Server URL is not configured.")
        
        url = f"{self.server_url}{endpoint}"
        response = requests.get(url, headers=self.get_headers(), params=params)
        response.raise_for_status()
        return response.json()
