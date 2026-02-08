import logging
import requests
import pandas as pd
from tabulate import tabulate

from mono_engine.config import Config
from mono_engine.core.session import Session

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = Config.load('config.yaml')
session = Session(config)

two_fa = input("\nEnter FRESH 6-digit 2FA code (generate now!): ").strip()
if two_fa:
    session.config.credentials['two_fa'] = two_fa

if not session.login():
    print("Login failed — exiting")
else:
    print("LOGIN SUCCESSFUL — testing symbol store BFO fetch")

    base_url = "https://api.tradejini.com/v2"

    # Possible endpoints from SDK test files
    endpoints = [
        "/api/mkt-data/scrips/symbol-store/BFO",
        "/symbol-store/BFO",
        "/api/mkt-data/scrips/symbol-store/BFO",
    ]

    df = pd.DataFrame()

    for endpoint in endpoints:
        if not df.empty:
            break
        logging.info(f"Trying endpoint: {endpoint}")

        # Unauthenticated
        unauth_session = requests.Session()
        try:
            resp = unauth_session.get(base_url + endpoint)
            logging.info(f"Unauth status: {resp.status_code}")
            logging.info(f"Raw text: {resp.text}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    logging.info(f"JSON keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                    data = data.get("d", data) if isinstance(data, dict) else data
                except:
                    data = []
                df = pd.DataFrame(data)
                logging.info(f"Rows: {len(df)} | Columns: {list(df.columns)}")
        except Exception as e:
            logging.error(f"Unauth failed on {endpoint}: {e}")

        # If empty, try authenticated
        if df.empty:
            try:
                resp = session.rest.session.get(base_url + endpoint)
                logging.info(f"Auth status: {resp.status_code}")
                logging.info(f"Raw text: {resp.text}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        data = data.get("d", data) if isinstance(data, dict) else data
                    except:
                        data = []
                    df = pd.DataFrame(data)
                    logging.info(f"Auth rows: {len(df)} | Columns: {list(df.columns)}")
            except Exception as e:
                logging.error(f"Auth failed on {endpoint}: {e}")

    if df.empty:
        print("BFO fetch failed on all endpoints — no data")
    else:
        # Robust column selection
        token_col = next((col for col in ["excToken", "token", "contractToken", "exc_token"] if col in df.columns), "N/A")
        strike_col = next((col for col in ["strikePrice", "strike"] if col in df.columns), "N/A")
        option_type_col = next((col for col in ["optionType", "option_type"] if col in df.columns), "N/A")
        expiry_col = next((col for col in ["expiryDate", "expiry"] if col in df.columns), "N/A")
        underlying_col = next((col for col in ["underlying", "name"] if col in df.columns), "N/A")
        oi_col = next((col for col in ["OI", "openInterest"] if col in df.columns), "N/A")
        lot_col = next((col for col in ["lotSize", "lot_size"] if col in df.columns), "N/A")

        # Filter SENSEX or first 10
        sensex_df = df[df[underlying_col] == "SENSEX"].head(10) if underlying_col != "N/A" else df.head(10)

        table_data = []
        for _, row in sensex_df.iterrows():
            table_data.append({
                "excToken": row.get(token_col, "N/A"),
                "strikePrice": row.get(strike_col, "N/A"),
                "optionType": row.get(option_type_col, "N/A"),
                "expiryDate": row.get(expiry_col, "N/A"),
                "underlying": row.get(underlying_col, "N/A"),
                "OI": row.get(oi_col, "N/A"),
                "lotSize": row.get(lot_col, "N/A"),
            })

        print("\nFirst 10 BFO symbols (SENSEX if available):")
        print(tabulate(table_data, headers="keys", tablefmt="grid"))

    session.close()