"""
Historical Backtest - PURE SINGLE SYMBOL (Final Version with your requests)
- Quantity = 900 contracts (as requested)
- Total Contracts note (900 contracts = 45 lots of 20)
- Per-buy-reason profit/loss summary at the end
- Full date + time + Buy Reason
"""

import logging
import sqlite3
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from collections import defaultdict
from .base import BaseModule


class HistoricalBacktest(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.trades = []
        self.symbol = "SENSEX 05MAR 81200 PE"   # ← Change here if needed
        self.current_buy_reason = "unknown"

    def start(self):
        self.run()

    def stop(self):
        pass

    def run(self):
        self.logger.info("=" * 100)
        self.logger.info("🚀 HISTORICAL BACKTEST — PURE SINGLE SYMBOL MODE")
        self.logger.info(f"Symbol: {self.symbol}")
        self.logger.info("Real stoploss + forced sell safety at bar 500")
        self.logger.info("=" * 100)

        state_module = self.engine.modules.get('state')
        strategy_module = self.engine.modules.get('strategy')

        db_path = 'mono_engine_data.db'

        # ====================== LISTENERS ======================
        def on_buy_signal(data):
            if data.get('symbol') != self.symbol:
                return
            price = data.get('price')
            self.current_buy_reason = data.get('buy_reason', 'unknown')
            dummy_id = f"HIS-B-{int(datetime.now().timestamp())}"
            self.logger.info(f"BUY SIGNAL → {self.symbol} @ {price:.2f} | Reason: {self.current_buy_reason}")

            fill_data = {
                'order_id': dummy_id,
                'scrip': self.symbol,
                'order_type': 'buy',
                'price': price,
                'quantity': 900,                    # Fixed 900 contracts
                'fill_time': datetime.now()
            }
            self.engine.events.publish('order_filled', fill_data)

        def on_exit_signal(data):
            if data.get('symbol') != self.symbol:
                return
            exit_price = data.get('exit_price')
            reason = data.get('reason', 'unknown')
            dummy_id = f"HIS-S-{int(datetime.now().timestamp())}"
            self.logger.info(f"EXIT SIGNAL → {self.symbol} @ {exit_price:.2f} | Reason: {reason}")

            entry = state_module.get_entry_details(self.symbol)
            if entry:
                pnl_pct = round((exit_price - entry.price) / entry.price * 100, 2)
                trade = {
                    'Entry Time': entry.time.strftime('%Y-%m-%d %H:%M'),
                    'Entry Price': entry.price,
                    'Exit Time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'Exit Price': exit_price,
                    'Quantity': 900,                    # 900 contracts
                    'Buy Reason': self.current_buy_reason,
                    'Exit Reason': reason,
                    'PnL %': pnl_pct
                }
                self.trades.append(trade)
                self.logger.info(f"TRADE RECORDED | Buy Reason: {self.current_buy_reason} | PnL: {pnl_pct}%")

            fill_data = {
                'order_id': dummy_id,
                'scrip': self.symbol,
                'order_type': 'sell',
                'price': exit_price,
                'quantity': 900,
                'fill_time': datetime.now()
            }
            self.engine.events.publish('order_filled', fill_data)

        self.events.subscribe('buy_signal', on_buy_signal)
        self.events.subscribe('exit_signal', on_exit_signal)

        # ====================== LOAD & REPLAY ======================
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(f"""
            SELECT timestamp as ts, open, high, low, close, volume
            FROM historical_1min
            WHERE symbol = '{self.symbol}'
            ORDER BY timestamp
        """, conn, parse_dates=['ts'], index_col='ts')
        conn.close()

        if df.empty:
            self.logger.error(f"No data found for {self.symbol}!")
            return

        self.logger.info(f"Replaying {len(df)} bars for {self.symbol}...")
        df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low',
                                'close': 'Close', 'volume': 'Volume'})

        if self.symbol in strategy_module.strategies:
            strategy_module.strategies[self.symbol].reset_day()
        if self.symbol in state_module.states:
            state_module.states[self.symbol].update(in_trade=False)

        strategy = strategy_module._get_or_create_strategy(self.symbol)

        for i, (ts, row) in enumerate(df.iterrows()):
            strategy.on_data_update({'1min': df.loc[:ts].tail(100)})

            enter, price, reason = strategy.should_enter() if hasattr(strategy, 'should_enter') else (False, None, '')
            if enter:
                self.engine.events.publish('buy_signal', {
                    'price': price or 0.0,
                    'symbol': self.symbol,
                    'quantity': 900,
                    'buy_reason': reason
                })

            bar_data = {
                'symbol': self.symbol,
                'bar': {
                    'ts': ts,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
            }
            self.engine.events.publish('1min_bar_closed', bar_data)

            if i == 500 and state_module.is_in_trade(self.symbol):
                self.logger.info(f"FORCING SELL at bar 500 @ {row['Close']:.2f}")
                self.engine.events.publish('exit_signal', {
                    'symbol': self.symbol,
                    'exit_price': row['Close'],
                    'reason': 'FORCED_AFTER_500_BARS',
                    'time': ts,
                    'quantity': 900
                })

        # Cleanup
        self.events.unsubscribe('buy_signal', on_buy_signal)
        self.events.unsubscribe('exit_signal', on_exit_signal)

        # ====================== FINAL TABLE + SUMMARY ======================
        self.logger.info("=" * 100)
        self.logger.info("✅ SINGLE SYMBOL BACKTEST COMPLETED")
        self.logger.info("=" * 100)

        if self.trades:
            print("\nHistorical Trades (Single Symbol):")
            print(tabulate(self.trades, headers="keys", tablefmt="grid"))

            # Cumulative PnL
            total_pnl = sum(t['PnL %'] for t in self.trades)
            print(f"\n{'='*90}")
            print(f"TOTAL CONTRACTS TRADED : 900")
            print(f"CUMULATIVE P&L FOR ALL TRADES = {total_pnl:.2f}%")
            print(f"{'='*90}")

            # === Per Buy Reason Summary (Profit / Loss) ===
            reason_summary = defaultdict(lambda: {"trades": 0, "profit": 0.0, "loss": 0.0})
            for t in self.trades:
                r = t['Buy Reason']
                reason_summary[r]["trades"] += 1
                if t['PnL %'] > 0:
                    reason_summary[r]["profit"] += t['PnL %']
                else:
                    reason_summary[r]["loss"] += t['PnL %']

            print("\nPER BUY REASON SUMMARY (Profit / Loss)")
            print(f"{'Buy Reason':<40} {'Trades':<8} {'Profit %':<12} {'Loss %':<12} {'Net %':<10}")
            print("-" * 85)
            for r, s in reason_summary.items():
                net = s["profit"] + s["loss"]
                print(f"{r:<40} {s['trades']:<8} {s['profit']:>10.2f} {s['loss']:>12.2f} {net:>10.2f}")
            print("-" * 85)
        else:
            self.logger.warning("No trades recorded")
