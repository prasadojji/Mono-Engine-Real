import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from mono_engine.config import Config
from mono_engine.core.session import Session

config = Config.load('config.yaml')
print("Config loaded - using your real apikey/password")

session = Session(config)

# Prompt for fresh 2FA
two_fa = input("\nEnter CURRENT 6-digit 2FA code (generate fresh now!): ").strip()
if two_fa:
    session.config.credentials['two_fa'] = two_fa
    session.config.credentials['two_fa_typ'] = 'totp'

print("\nAttempting login...")
success = session.login()

if success:
    print("*** LOGIN SUCCESSFUL ***")
    # Test authenticated call (funds/limits from your old project)
    try:
        limits = session.rest.get("/api/oms/limits")
        print("Funds/Margins test succeeded:")
        data = limits.get("d", {})
        print(f"Available Cash: ₹{data.get('availCash', 0):.2f}")
        print(f"Available Margin: ₹{data.get('availMargin', 0):.2f}")
    except Exception as e:
        print("Test call error:", e)
else:
    print("Login failed - see logs")