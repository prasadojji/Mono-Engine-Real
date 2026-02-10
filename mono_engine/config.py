import os
from pathlib import Path
from typing import List, Dict, Any

import yaml


class Config:
    """
    Centralized configuration for MonoEngine (Tradejini Mono API).
    Loads from YAML file first, then overrides with environment variables.
    two_fa and two_fa_typ are optional (prompted at runtime).
    """

    def __init__(self, data: Dict[str, Any]):
        self.credentials = data.get('credentials', {})
        self.endpoints = data.get('endpoints', {
            'base_url': 'https://api.tradejini.com/v2',
            'ws_url': 'wss://api.tradejini.com/ws',
        })
        self.enabled_modules: List[str] = data.get('enabled_modules', [
            'order', 'portfolio', 'market_data'
        ])
        self.logging_level: str = data.get('logging_level', 'INFO')
        self.other: Dict[str, Any] = data.get('other', {})

        # Only require apikey and password (two_fa prompted fresh each time)
        required = ['apikey', 'password']
        missing = [k for k in required if k not in self.credentials or not self.credentials[k]]
        if missing:
            raise ValueError(f"Missing required Tradejini credentials in config: {missing}")
        
    def get(self, key, default=None):
        """General get method to search all config attributes/dicts."""
        # Check root attributes first
        if hasattr(self, key):
            return getattr(self, key, default)
        # Search sub-dicts like credentials, endpoints, other
        for attr in ['credentials', 'endpoints', 'other']:
            if hasattr(self, attr):
                val = getattr(self, attr)
                if isinstance(val, dict) and key in val:
                    return val.get(key, default)
        return default

    @classmethod
    def load(cls, config_path: str = 'config.yaml') -> 'Config':
        data: Dict[str, Any] = {}

        # Load from YAML
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                yaml_data = yaml.safe_load(f) or {}
            data.update(yaml_data)

        # Override with env vars
        env_map = {
            'apikey': 'TRADEJINI_APIKEY',
            'password': 'TRADEJINI_PASSWORD',
        }
        credentials = data.get('credentials', {})
        for key, env_var in env_map.items():
            if env_var in os.environ:
                credentials[key] = os.environ[env_var]
        data['credentials'] = credentials

        if 'MONO_ENABLED_MODULES' in os.environ:
            data['enabled_modules'] = [m.strip() for m in os.environ['MONO_ENABLED_MODULES'].split(',')]

        if 'MONO_LOGGING_LEVEL' in os.environ:
            data['logging_level'] = os.environ['MONO_LOGGING_LEVEL']

        return cls(data)

    def __repr__(self):
        return f"<Config modules={self.enabled_modules} base_url={self.endpoints.get('base_url')}>"