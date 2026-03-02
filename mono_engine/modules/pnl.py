"""
PnL Engine Module - Production Grade
- Independent, event-driven, zero strategy logic
- Tracks realized + unrealized + per-buy-reason win-rate
- Works identically in paper & real mode
- Console table every 10s + CSV persistence
"""

import logging
import time
import csv
import os
from collections import defaultdict
from datetime import datetime
from threading import Thread, Event
import sqlite3
import pandas as pd
from .base import BaseModule


class PnLModule(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.market_data = None
        self.state = None
        self.open_trades = {}
        self.realized_history = []
        self.per_reason = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0.0, "trades": 0})
        self.pending_buy_reasons = {}
        self.current_ltp = {}
        self.db_path = 'mono_engine_data.db'
        self.csv_path = 'pnl_trades.csv'
        self._stop_summary = Event()
        self.summary_thread = None
        self.is_historical_run = False
        self._init_db()
        self.logger.info("PnLModule initialized (per-buy-reason win-rate + 10s table)")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                symbol TEXT,
                buy_reason TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity INTEGER,
                lot_size INTEGER,
                entry_time TEXT,
                exit_time TEXT,
                realized_pnl REAL DEFAULT 0,
                is_historical INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        self.logger.info("PnL database ready (trades table created)")

    def _load_realized_history(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM trades", conn)
        conn.close()
        for _, row in df.iterrows():
            trade = row.to_dict()
            self.realized_history.append(trade)
            r = trade.get('buy_reason', 'unknown')
            pnl = float(trade.get('realized_pnl', 0))
            self.per_reason[r]['trades'] += 1
            self.per_reason[r]['total_pnl'] += pnl
            if pnl > 0:
                self.per_reason[r]['wins'] += 1
            else:
                self.per_reason[r]['losses'] += 1

    def _append_to_db(self, trade, is_historical=False):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''INSERT OR REPLACE INTO trades VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (
            trade.get('trade_id'), trade.get('symbol'), trade.get('buy_reason'),
            trade.get('entry_price'), trade.get('exit_price'), trade.get('quantity'),
            trade.get('lot_size'), str(trade.get('entry_time')), str(trade.get('exit_time')),
            trade.get('realized_pnl', 0), 1 if is_historical else 0
        ))
        conn.commit()
        conn.close()

    def start(self):
        self.market_data = self.engine.modules.get('market_data')
        self.state = self.engine.modules.get('state')
        self.events.subscribe('order_filled', self._on_order_filled)
        self.events.subscribe('on_tick', self._on_tick)
        self.events.subscribe('buy_signal', self._on_buy_signal)
        self.summary_thread = Thread(target=self._summary_loop, daemon=True)
        self.summary_thread.start()
        self.logger.info("PnLModule started — listening for fills & ticks")

    def stop(self):
        self._stop_summary.set()
        if self.summary_thread and self.summary_thread.is_alive():
            self.summary_thread.join(timeout=2)
        self.events.unsubscribe('order_filled', self._on_order_filled)
        self.events.unsubscribe('on_tick', self._on_tick)
        self.events.unsubscribe('buy_signal', self._on_buy_signal)
        self.logger.info("PnLModule stopped")

    def _on_buy_signal(self, data):
        symbol = data.get('symbol') or data.get('subscribed_symbol')
        reason = data.get('buy_reason', 'unknown')
        if symbol:
            self.pending_buy_reasons[symbol] = (reason, time.time())

    def _on_order_filled(self, data):
        order_id = data.get('order_id')
        symbol = data.get('scrip') or data.get('symbol')
        side = data.get('order_type', '').lower()
        price = data.get('price')
        qty = data.get('quantity', 0)
        fill_time = data.get('fill_time', datetime.now())

        if not all([order_id, symbol, price is not None, qty]):
            return

        if side == 'buy':
            reason = 'unknown'
            if symbol in self.pending_buy_reasons:
                r, ts = self.pending_buy_reasons[symbol]
                if time.time() - ts < 10:
                    reason = r
                del self.pending_buy_reasons[symbol]

            lot = self._get_lot_size(symbol)
            trade = {
                'trade_id': order_id,
                'symbol': symbol,
                'buy_reason': reason,
                'entry_price': float(price),
                'quantity': int(qty),
                'lot_size': lot,
                'entry_time': fill_time,
                'status': 'open'
            }
            self.open_trades[order_id] = trade

        elif side == 'sell':
            for tid, t in list(self.open_trades.items()):
                if t['symbol'] == symbol:
                    trade = t
                    exit_price = float(price)
                    realized_pnl = (exit_price - trade['entry_price']) * trade['lot_size'] * trade['quantity']
                    trade['exit_price'] = exit_price
                    trade['exit_time'] = fill_time
                    trade['realized_pnl'] = realized_pnl
                    trade['status'] = 'closed'
                    self.realized_history.append(trade)
                    del self.open_trades[tid]
                    r = trade['buy_reason']
                    self.per_reason[r]['trades'] += 1
                    self.per_reason[r]['total_pnl'] += realized_pnl
                    if realized_pnl > 0:
                        self.per_reason[r]['wins'] += 1
                    else:
                        self.per_reason[r]['losses'] += 1
                    self._append_to_db(trade)
                    break

    def _on_tick(self, data):
        symbol = data.get('symbol') or data.get('scrip')
        ltp = data.get('ltp') or data.get('close')
        if symbol and ltp is not None:
            self.current_ltp[symbol] = float(ltp)

    def _get_lot_size(self, symbol: str) -> int:
        if self.market_data:
            if hasattr(self.market_data, 'lot_sizes') and symbol in self.market_data.lot_sizes:
                return self.market_data.lot_sizes[symbol]
            if hasattr(self.market_data, 'quotes') and symbol in self.market_data.quotes:
                q = self.market_data.quotes[symbol]
                if 'lot' in q:
                    return int(q['lot'])
        return 10

    def _get_readable_symbol(self, token: str) -> str:
        if self.market_data and hasattr(self.market_data, 'quotes') and token in self.market_data.quotes:
            q = self.market_data.quotes[token]
            if 'symbol' in q and q['symbol']:
                return q['symbol']
        return token.replace('_BFO', '').replace('_BSE', '')

    def _summary_loop(self):
        while not self._stop_summary.is_set():
            self._print_pnl_table()
            self._stop_summary.wait(10)

    def _print_pnl_table(self):
        live_pnl = self.get_total_live_pnl()
        unreal = self._calculate_unrealized()
        realized = live_pnl - unreal
        open_count = len(self.open_trades)

        print("\n" + "="*120)
        print(f"🔥 MoNo PnL LIVE @ {datetime.now().strftime('%H:%M:%S')} | "
              f"Total: ₹{live_pnl:,.0f} | Realized: ₹{realized:,.0f} | Unrealized: ₹{unreal:,.0f} | Open: {open_count}")
        print("="*120)

        print("PER-SYMBOL PROFIT/LOSS (with Buy/Sell Reason)")
        print(f"{'Symbol':<30} {'Buy Reason':<25} {'Entry':<10} {'Exit/LTP':<10} {'Qty':<6} {'Lot':<5} {'PnL ₹':<12} {'%':<8} {'Status'}")
        print("-"*120)

        # Closed trades
        for t in self.realized_history:
            sym = self._get_readable_symbol(t['symbol'])
            exit_p = t.get('exit_price', 0)
            pnl = t.get('realized_pnl', 0)
            pct = ((exit_p - t['entry_price']) / t['entry_price'] * 100) if t['entry_price'] else 0
            print(f"{sym:<30} {t['buy_reason']:<25} {t['entry_price']:<10.2f} {exit_p:<10.2f} "
                  f"{t['quantity']:<6} {t['lot_size']:<5} ₹{pnl:,.0f} {pct:6.1f}% Closed")

        # Open trades with live LTP
        for t in self.open_trades.values():
            sym = self._get_readable_symbol(t['symbol'])
            ltp = self.current_ltp.get(t['symbol'], t['entry_price'])
            unreal = (ltp - t['entry_price']) * t['lot_size'] * t['quantity']
            pct = ((ltp - t['entry_price']) / t['entry_price'] * 100) if t['entry_price'] else 0
            print(f"{sym:<30} {t['buy_reason']:<25} {t['entry_price']:<10.2f} {ltp:<10.2f} "
                  f"{t['quantity']:<6} {t['lot_size']:<5} ₹{unreal:,.0f} {pct:6.1f}% Open")

        if self.per_reason:
            print("\nPER BUY-REASON PERFORMANCE (Closed Trades)")
            print(f"{'Reason':<35} {'Trades':<6} {'Wins':<5} {'Win%':<6} {'Total PnL':<12}")
            print("-"*70)
            for reason, stats in self.per_reason.items():
                winrate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] else 0
                print(f"{reason:<35} {stats['trades']:<6} {stats['wins']:<5} "
                      f"{winrate:5.1f}%  ₹{stats['total_pnl']:,.0f}")

        print("="*120 + "\n")

    def get_total_live_pnl(self) -> float:
        realized = sum(t.get('realized_pnl', 0) for t in self.realized_history)
        unreal = self._calculate_unrealized()
        return realized + unreal

    def _calculate_unrealized(self) -> float:
        total = 0.0
        for trade in self.open_trades.values():
            ltp = self.current_ltp.get(trade['symbol'])
            if ltp is not None:
                pnl = (ltp - trade['entry_price']) * trade['lot_size'] * trade['quantity']
                total += pnl
        return total