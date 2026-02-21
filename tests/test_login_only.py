# test_login_only.py - Minimal login test
import logging
from mono_engine.config import Config
from mono_engine.core.session import Session

logging.basicConfig(level=logging.INFO)

config = Config.load('config.yaml')
session = Session(config)

if session.login():
    print("LOGIN SUCCESS — Access token:", session.access_token)
    print("Auth header set in rest client.")
else:
    print("Login failed.")