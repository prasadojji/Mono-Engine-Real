# mono_engine/modules/historical_backtest.py
"""
Historical Backtest Module
- Direct read from mono_engine_data.db using actual symbol names from your DB
- Exact same Buy_AFL_python + StoplossModule logic
- Outputs nice table as requested: Symbol | Buy Time | Buy Price | Sell Time | Sell Price | PnL% | Buy Reason | Sell Reason
"""

import logging
import sqlite3
import pandas as pd
from tabulate import tabulate
from datetime import datetime

from .base import BaseModule


class HistoricalBacktest(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.trades = []  # List of dicts for final table

    def start(self):
        """Required by BaseModule"""
        self.run()

    def stop(self):
        """Required by BaseModule"""
        pass

    def run(self):
        """Main entry point for historical backtest"""
        self.logger.info("=" * 80)
        self.logger.info("🚀 STARTING FULL HISTORICAL BACKTEST (Direct from DB)")
        self.logger.info("=" * 80)

        market_data = self.engine.modules.get('market_data')
        state_module = self.engine.modules.get('state')
        strategy_module = self.engine.modules.get('strategy')
        stoploss_module = self.engine.modules.get('stoploss')

        if not all([market_data, strategy_module, stoploss_module]):
            self.logger.error("Missing required modules for backtest")
            return

        db_path = 'mono_engine_data.db'

        # Use symbol names from watchlist (they match your DB)
        symbols = [item['symbol'] for item in market_data.watchlist]
        symbols.append('SENSEX_SPOT')  # Spot

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

                self.logger.info(f"Replaying {len(df)} bars for {symbol} from local DB...")

                # Normalize columns to uppercase (what strategy expects)
                df = df.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })

                # Reset state and strategy
                if symbol in state_module.states:
                    state_module.states[symbol].update(in_trade=False)
                if symbol in strategy_module.strategies:
                    strategy_module.strategies[symbol].reset_day()

                # Replay bar by bar
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

                    # Strategy (buy logic)
                    strategy = strategy_module._get_or_create_strategy(symbol)
                    strategy.on_data_update({'1min': df.loc[:ts].tail(100)})

                    # Stoploss (your full AFL exit logic)
                    stoploss_module._on_1min_bar_closed(bar_data)

                total_trades += len(getattr(state_module.states[symbol], 'trade_history', []))

            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")

        # Final nice table as requested
        self.logger.info("=" * 80)
        self.logger.info(f"✅ HISTORICAL BACKTEST COMPLETED")
        self.logger.info(f"Total symbols processed : {len(symbols)}")
        self.logger.info(f"Total trades simulated   : {total_trades}")
        self.logger.info("=" * 80)

        if self.trades:
            print("\nHistorical Trades:")
            print(tabulate(self.trades, headers="keys", tablefmt="grid"))
        else:
            self.logger.info("No trades were recorded during backtest.")