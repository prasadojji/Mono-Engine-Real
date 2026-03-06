import logging
import pandas as pd
import sqlite3
import yaml
from datetime import datetime
from collections import defaultdict
from tabulate import tabulate  # pip install tabulate if needed
import json
import re  # For parsing description
from mono_engine.modules.stoploss import StoplossModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config (for stoploss params)
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

quantity = config.get('stoploss_params', {}).get('quantity', 900)

# Load historical_symbols.json
with open('historical_symbols.json', 'r') as f:
    historical_data = json.load(f)

# Parse for simulation: Extract symbol, db_symbol (id), expiry, and from description: date, buy_price
parsed_entries = []
for item in historical_data:
    if item.get('symbol') == 'SENSEX_SPOT':
        continue  # Skip spot
    symbol = item.get('symbol')
    db_symbol = item.get('id')
    expiry = item.get('expiry', 'N/A')
    description = item.get('description')
    # Parse "ATM for YYYY-MM-DD open PRICE"
    match = re.search(r'ATM for (\d{4}-\d{2}-\d{2}) open ([\d.]+)', description)
    if match:
        date_str = match.group(1)
        buy_price = float(match.group(2))
        parsed_entries.append((symbol, db_symbol, expiry, date_str, buy_price))

# Connect to DB
conn = sqlite3.connect('mono_engine_data.db')

# Function to load ALL 1-min data for the symbol (ignore start_date since data may be older)
def load_data(db_symbol):
    query = """
        SELECT timestamp as time, open, high, low, close, volume 
        FROM historical_1min 
        WHERE symbol = ? 
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn, params=(db_symbol,))
    if df.empty:
        return df
    df['time'] = pd.to_datetime(df['time'])
    return df.set_index('time')

# Mock engine with event bus
class MockEngine:
    def __init__(self, config):
        self.config = config
        self.events = defaultdict(list)

    def subscribe(self, event, handler):
        self.events[event].append(handler)

    def publish(self, event, data):
        for handler in self.events.get(event, []):
            handler(data)

# Simulate for each parsed entry
trades = []
sno = 1
sell_triggered = False

def on_sell_signal(event):
    global sell_triggered
    sell_triggered = True

for symbol, db_symbol, expiry, date_str, buy_price in parsed_entries:
    logger.info(f"Processing historical buy for {symbol} on {date_str} at {buy_price}")
    try:
        df_1min = load_data(db_symbol)
        if df_1min.empty:
            logger.warning(f"No data for {symbol} (db_symbol: {db_symbol})")
            continue

        logger.info(f"Loaded {len(df_1min)} 1-min bars for {symbol}")

        mock_engine = MockEngine(config)
        stoploss = StoplossModule(mock_engine)

        # Subscribe to exit_signal
        mock_engine.subscribe('exit_signal', on_sell_signal)

        # Start position at buy
        entry_time = df_1min.index[0] if not df_1min.empty else datetime.strptime(date_str, '%Y-%m-%d')  # Use first available time
        in_position = True

        mock_engine.publish('state_updated', {
            'symbol': symbol,
            'in_trade': True,
            'entry_price': buy_price
        })

        logger.info(f"Simulated buy for {symbol} at {entry_time} price {buy_price}")

        # Feed all 1-min ticks from entry onward
        sell_price = None
        sell_time = None
        for tick_idx, tick in df_1min.iterrows():
            sell_triggered = False
            mock_engine.publish('on_tick', {
                'symbol': symbol,
                'ltp': tick['close'],
                'candle': tick.to_dict()
            })

            if sell_triggered:
                sell_price = tick['close']
                sell_time = tick_idx
                break

        if sell_price is None:
            # No sell, use last close
            last_price = df_1min['close'].iloc[-1]
            pnl = (last_price - buy_price) * quantity
            trades.append({
                'sno': sno,
                'symbol': symbol,
                'date': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'expiry': expiry,
                'buy_price': buy_price,
                'sell_price': f"No Sell (Last Close: {last_price})",
                'pnl': pnl
            })
        else:
            pnl = (sell_price - buy_price) * quantity
            trades.append({
                'sno': sno,
                'symbol': symbol,
                'date': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'expiry': expiry,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'sell_time': sell_time.strftime('%Y-%m-%d %H:%M:%S'),
                'pnl': pnl
            })
        sno += 1

    except Exception as e:
        logger.error(f"Error processing {symbol}: {e}")

conn.close()

# Sort by date descending
trades.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'), reverse=True)

# Output grid
if trades:
    df_trades = pd.DataFrame(trades)
    print(tabulate(df_trades, headers='keys', tablefmt='grid', showindex=False))
else:
    print("No trades generated from historical data.")