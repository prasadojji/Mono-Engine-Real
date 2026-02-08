from mono_engine.config import Config

# Load the config (uses config.yaml by default)
try:
    config = Config.load('config.yaml')
    print("Config loaded successfully!")
    print(config)
    print("\nEnabled modules:", config.enabled_modules)
    print("Logging level:", config.logging_level)
    print("Base URL:", config.endpoints.get('base_url'))
except ValueError as e:
    print("Config error (expected with dummy credentials):", e)
except Exception as e:
    print("Unexpected error:", e)