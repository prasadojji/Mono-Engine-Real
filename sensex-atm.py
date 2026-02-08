import csv
from io import StringIO
from datetime import datetime, date
import threading
import time
import re  # For fixing small SDK warning (optional but recommended)

# Your existing project imports — adjust paths if needed
from mono_engine.config import Config
from mono_engine.core.session import Session  # Change if Session is in different folder
from nxtradstream import NxtradStream  # From your installed SDK

# Optional: Fix SDK warning (add this if you see SyntaxWarning)
def commafmt(value, precision=2):
    v = str(round(float(value), precision))
    parts = v.split(".")
    parts[0] = re.sub(r"\B(?=(\d{3})+(?!\d))", ",", parts[0])
    return ".".join(parts)

def find_sensex_atm_options(config: Config, timeout: int = 180) -> dict:
    """
    Gets Sensex ATM Call & Put tokens based on today's open price.
    Uses your Mono Engine Session + Tradejini SDK.
    Run only during market hours (9:15 AM to 3:30 PM IST).
    """
    # Reset variables
    index_token = None
    index_exch_seg = "BSE"
    sensex_options = []

    # 1. Login using your existing Session
    session = Session(config)
    if not session.is_logged_in():
        print("Logging in...")
        if not session.login():
            raise ValueError("Login failed — check credentials")
    
    rest = session.rest
    apikey = config.credentials['apikey']

    # Get access_token — you will add one line in Session class (see Step 2 below)
    access_token = getattr(session.rest, 'access_token', None) or getattr(session, 'access_token', None)
    if not access_token:
        raise ValueError("No access_token found. Add 'self.access_token = access_token' in Session.login()")

    # 2. Download scrip master files
    groups_url = "/api/mkt-data/scrips/symbol-store"
    groups_resp = rest.get(groups_url)
    if not groups_resp.ok:
        raise ValueError("Cannot get scrip groups")

    groups = groups_resp.json()
    print("Found scrip groups:", groups)

    for group in groups:
        url = f"/api/mkt-data/scrips/symbol-store/{group}"
        resp = rest.get(url, headers={"Accept": "text/plain"})
        if not resp.ok:
            continue

        csv_data = StringIO(resp.text)
        reader = csv.DictReader(csv_data)

        print(f"Columns in {group}: {reader.fieldnames}")

        for row in reader:
            symbol = (row.get('tradingSymbol') or row.get('symbol') or '').upper()
            if 'SENSEX' not in symbol:
                continue

            token = row.get('exchToken') or row.get('token') or ''
            if not token:
                continue

            instrument = row.get('instrumentType', '').upper()

            if instrument == 'INDEX':
                index_token = token
                index_exch_seg = 'BSE'
                print(f"Sensex Index found → Token: {token}_BSE | Symbol: {symbol}")

            elif 'OPT' in instrument:
                # Strike
                strike_str = row.get('strikePrice', '0').replace(',', '')
                try:
                    strike = float(strike_str)
                    if strike > 100000:  # Sometimes scaled
                        strike /= 100
                except:
                    strike = 0.0

                # Option type
                opt_type = row.get('optionType', '').upper()

                # Expiry
                expiry_str = row.get('expiryDate', '')
                exp_date = None
                for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d%b%Y"):
                    try:
                        exp_date = datetime.strptime(expiry_str.strip().upper(), fmt).date()
                        break
                    except:
                        pass
                if not exp_date:
                    continue

                sensex_options.append({
                    'token': token,
                    'exch_seg': 'BFO',
                    'strike': strike,
                    'option_type': opt_type,
                    'expiry': exp_date,
                    'symbol': symbol
                })

    if not index_token:
        raise ValueError("Sensex index not found in scrip data")

    print(f"Found {len(sensex_options)} Sensex option contracts")

    # 3. WebSocket to get today's open price
    auth_token = f"{apikey}:{access_token}"
    open_captured = threading.Event()
    result_data = {'open_price': None}

    def on_connect(stream, ev):
        if ev['s'] == 'connected':
            sym = f"{index_token}_{index_exch_seg}"
            print(f"Streaming Sensex index: {sym}")
            stream.subscribeL1SnapShot([sym])
            stream.subscribeL1([sym])

    def on_stream(stream, data):
        if data.get('msgType') == 'L1' and str(data.get('token')) == index_token:
            open_price = data.get('open')
            if open_price and open_price > 0 and result_data['open_price'] is None:
                result_data['open_price'] = open_price
                print(f"\n=== Sensex Open Price: {open_price} ===\n")

                # Find ATM
                today = date.today()
                active_opts = [o for o in sensex_options if o['expiry'] >= today]
                if not active_opts:
                    print("No active options")
                    open_captured.set()
                    return

                nearest_expiry = min(o['expiry'] for o in active_opts)
                expiry_opts = [o for o in active_opts if o['expiry'] == nearest_expiry]

                strikes = {o['strike'] for o in expiry_opts if o['strike'] > 0}
                atm_strike = min(strikes, key=lambda s: abs(s - open_price))

                ce = next((o for o in expiry_opts if o['option_type'] == 'CE' and o['strike'] == atm_strike), None)
                pe = next((o for o in expiry_opts if o['option_type'] == 'PE' and o['strike'] == atm_strike), None)

                result_data.update({
                    'expiry': nearest_expiry.strftime('%d-%b-%Y'),
                    'atm_strike': atm_strike,
                    'ce_token': f"{ce['token']}_BFO" if ce else None,
                    'pe_token': f"{pe['token']}_BFO" if pe else None,
                    'ce_symbol': ce['symbol'] if ce else None,
                    'pe_symbol': pe['symbol'] if pe else None
                })

                print(f"Nearest Expiry : {result_data['expiry']}")
                print(f"ATM Strike     : {atm_strike}")
                print(f"ATM CE Token   : {result_data['ce_token']} ({result_data['ce_symbol']})")
                print(f"ATM PE Token   : {result_data['pe_token']} ({result_data['pe_symbol']})")

                # Subscribe to live data for ATM options (optional)
                sub = []
                if ce: sub.append(result_data['ce_token'])
                if pe: sub.append(result_data['pe_token'])
                if sub:
                    stream.subscribeL1(sub)

                open_captured.set()

    nx = NxtradStream("api.tradejini.com", stream_cb=on_stream, connect_cb=on_connect)
    nx.connect(auth_token)

    print("Waiting for open price (max", timeout, "seconds)...")
    if not open_captured.wait(timeout=timeout):
        print("Timeout — no open price received")
        nx.disconnect()
        return None

    nx.disconnect()
    return result_data

# Test call (remove or comment out when integrating)
if __name__ == "__main__":
    # This matches how your Config class is meant to be used
    try:
        config = Config.load('config.yaml')  # Looks for config.yaml in the same folder
        print("Config loaded successfully:", config)
    except FileNotFoundError:
        print("config.yaml not found in project folder. Create it or use env vars.")
        exit(1)
    except ValueError as e:
        print("Config error:", e)
        exit(1)

    result = find_sensex_atm_options(config, timeout=180)
    if result:
        print("\n=== FINAL SENSEX ATM RESULT ===")
        print(result)
    else:
        print("No result (timeout or market closed)")