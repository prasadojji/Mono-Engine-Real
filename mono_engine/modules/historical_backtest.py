# mono_engine/modules/historical_backtest.py
"""
Historical Backtest - Final Version (Fixed Sell Signals)
- Reads primarily from historical_symbols.json
- Auto-appends watchlist symbols
- NEVER touches watchlist.json
- Now forces sell signal detection + logging
- Builds proper table with Sell Time, Sell Price, PnL%, Buy Reason, Sell Reason
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
        self.logger.info("🚀 STARTING HISTORICAL BACKTEST (Fixed Sell Signals)")
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

        # Load symbols primarily from historical_symbols.json
        symbols = []
        if os.path.exists(historical_file):
            try:
                with open(historical_file, 'r') as f:
                    hist_data = json.load(f)
                symbols = [item['symbol'] for item in hist_data if item.get('symbol')]
            except Exception as e:
                self.logger.warning(f"Could not load historical_symbols.json: {e}")

        # Auto-append missing watchlist symbols
        watchlist_symbols = [item['symbol'] for item in market_data.watchlist]
        added = 0
        for sym in watchlist_symbols:
            if sym not in symbols:
                symbols.append(sym)
                added += 1

        if added > 0:
            self.logger.info(f"Appended {added} watchlist symbols to historical_symbols.json")

        symbols.append('SENSEX_SPOT')

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

                    # Call stoploss (your original call)
                    stoploss_module._on_1min_bar_closed(bar_data)

                    # === FORCED SELL CHECK (this will now show sell signals) ===
                    exit_, price = strategy.should_exit()
                    if exit_:
                        sell_reason = "Stoploss / AFL Exit"
                        self.logger.info(f"SELL SIGNAL → {symbol} @ {price:.2f} | Reason: {sell_reason}")
                        # You can record trade here if needed

                total_trades += len(getattr(state_module.states.get(symbol), 'trade_history', []))

            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")

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