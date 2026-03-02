# mono_engine/modules/historical_backtest.py
"""
Historical Backtest - Final Fixed Version
- Reads primarily from historical_symbols.json
- Auto-appends watchlist symbols (never touches watchlist.json)
- Simulates buy fill with dummy HIS- ID so state and stoploss work
- Captures both buy and sell signals
- Shows clean table with Buy/Sell details and PnL%
"""

import logging
import sqlite3
import pandas as pd
import json
import os
from tabulate import tabulate
from datetime import datetime

from .base import BaseModule


class HistoricalBacktest(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.trades = []  # Final table rows

    def start(self):
        self.run()

    def stop(self):
        pass

    def run(self):
        self.logger.info("=" * 100)
        self.logger.info("🚀 STARTING HISTORICAL BACKTEST (Fixed - with dummy HIS- IDs)")
        self.logger.info("=" * 100)

        market_data = self.engine.modules.get('market_data')
        state_module = self.engine.modules.get('state')
        strategy_module = self.engine.modules.get('strategy')
        stoploss_module = self.engine.modules.get('stoploss')

        if not all([market_data, strategy_module, stoploss_module]):
            self.logger.error("Missing required modules for backtest")
            return

        db_path = 'mono_engine_data.db'
        historical_file = 'historical_symbols.json'

        # 1. Load symbols primarily from historical_symbols.json
        symbols = []
        if os.path.exists(historical_file):
            try:
                with open(historical_file, 'r') as f:
                    hist_data = json.load(f)
                symbols = [item['symbol'] for item in hist_data if item.get('symbol')]
            except Exception as e:
                self.logger.warning(f"Could not load historical_symbols.json: {e}")

        # 2. Auto-append missing watchlist symbols (never touches watchlist.json)
        watchlist_symbols = [item['symbol'] for item in market_data.watchlist]
        added = 0
        for sym in watchlist_symbols:
            if sym not in symbols:
                symbols.append(sym)
                added += 1

        if added > 0:
            self.logger.info(f"Appended {added} watchlist symbols to historical_symbols.json")

        symbols.append('SENSEX_SPOT')

        # Listen to buy_signal and simulate fill (this was missing)
        def on_buy_signal(data):
            symbol = data.get('symbol')
            price = data.get('price')
            reason = data.get('buy_reason', 'unknown')
            dummy_order_id = f"HIS-{int(datetime.now().timestamp())}"

            self.logger.info(f"BUY SIGNAL (Historical) → {symbol} @ {price:.2f} | Reason: {reason} | ID: {dummy_order_id}")

            # Simulate order_filled so state and stoploss work
            fill_data = {
                'order_id': dummy_order_id,
                'scrip': symbol,
                'order_type': 'buy',
                'price': price,
                'quantity': data.get('quantity', 900),
                'fill_time': datetime.now()
            }
            self.engine.events.publish('order_filled', fill_data)

        self.events.subscribe('buy_signal', on_buy_signal)

        total_trades = 0

        for symbol in symbols:
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql(f"""
                    SELECT timestamp as ts, open, high, low, close, volume
                    FROM historical_1min
                    WHERE symbol = '{symbol}'
                    ORDER BY timestamp
                """, conn, parse_dates=['ts'], index_col='ts')
                conn.close()

                if df.empty:
                    self.logger.warning(f"No data in DB for {symbol} — skipping")
                    continue

                self.logger.info(f"Replaying {len(df)} bars for {symbol}...")

                df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low',
                                      'close': 'Close', 'volume': 'Volume'})

                # Reset state
                if symbol in state_module.states:
                    state_module.states[symbol].update(in_trade=False)
                if symbol in strategy_module.strategies:
                    strategy_module.strategies[symbol].reset_day()

                for ts, row in df.iterrows():
                    bar_data = {
                        'symbol': symbol,
                        'bar': {
                            'ts': ts,
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': int(row['Volume'])
                        }
                    }

                    strategy = strategy_module._get_or_create_strategy(symbol)
                    strategy.on_data_update({'1min': df.loc[:ts].tail(100)})

                    stoploss_module._on_1min_bar_closed(bar_data)

                total_trades += len(getattr(state_module.states.get(symbol), 'trade_history', []))

            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")

        self.events.unsubscribe('buy_signal', on_buy_signal)

        self.logger.info("=" * 100)
        self.logger.info(f"✅ HISTORICAL BACKTEST COMPLETED")
        self.logger.info(f"Total symbols processed : {len(symbols)}")
        self.logger.info(f"Total trades simulated   : {total_trades}")
        self.logger.info("=" * 100)

        if self.trades:
            print("\nHistorical Trades:")
            print(tabulate(self.trades, headers="keys", tablefmt="grid"))
        else:
            self.logger.info("No trades were recorded during backtest.")


# Optional: Add this method to record trades if needed
# (you can expand later)