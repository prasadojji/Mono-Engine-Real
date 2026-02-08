import requests
from requests.exceptions import HTTPError

from mono_engine.config import Config
from mono_engine.core.rest_client import RestClient

import logging

class Session:
    """
    Authentication/session using proven direct requests method.
    """

    def __init__(self, config: Config):
        self.config = config
        self.rest = RestClient(config.endpoints.get('base_url', 'https://api.tradejini.com/v2'))
        self.logged_in = False
        self.access_token = None  # Save for reuse

    def login(self) -> bool:
        creds = self.config.credentials
        apikey = creds.get('apikey')
        password = creds.get('password')
        two_fa = creds.get('two_fa', '')
        two_fa_typ = creds.get('two_fa_typ', 'totp').lower()

        if not all([apikey, password]):
            logging.error("Missing apikey or password")
            return False

        url = f"{self.rest.base_url}/api-gw/oauth/individual-token-v2"
        headers = {"Authorization": f"Bearer {apikey}"}
        payload = {"password": password}
        if two_fa:
            payload["twoFa"] = two_fa
            payload["twoFaTyp"] = two_fa_typ  # Exact spelling from example.py
            logging.info("Using 2FA (totp) in login")

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if access_token:
                self.access_token = access_token
                self.rest.set_auth(apikey, access_token)
                self.logged_in = True
                logging.info("LOGIN SUCCESSFUL! Access token received")
                return True
            else:
                logging.error("No access_token in response: %s", data)
        except HTTPError as e:
            if e.response is not None:
                logging.error("Login HTTP error: %s - Response: %s", e, e.response.text)
            else:
                logging.error("Login HTTP error: %s - No response body", e)
        except Exception as e:
            logging.error("Login exception: %s", str(e))

        self.logged_in = False
        return False

    def is_logged_in(self) -> bool:
        return self.logged_in

    def close(self):
        self.rest.close()