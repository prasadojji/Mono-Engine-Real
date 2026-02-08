import requests
from typing import Optional, Dict, Any

class RestClient:
    """
    Reliable wrapper using direct requests (matches your working old project).
    Handles session, headers, and common calls.
    """

    def __init__(self, base_url: Optional[str] = "https://api.tradejini.com/v2"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.apikey: Optional[str] = None

    def set_auth(self, apikey: str, access_token: str) -> None:
        self.apikey = apikey
        self.access_token = access_token
        auth_token = f"{apikey}:{access_token}"
        self.session.headers.update({
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json"
        })

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, data=data, json=json, timeout=20)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.session.close()