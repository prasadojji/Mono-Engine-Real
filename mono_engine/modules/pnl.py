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

from .base import BaseModule


class PnLModule(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.market_data = None
        self.state = None

        # Core data
        self.open_trades = {}                    # trade_id -> trade_dict
        self.realized_history = []               # list of closed trades
        self.per_reason = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0.0, "trades": 0})

        # Pending reason capture (from buy_signal before fill)
        self.pending_buy_reasons = {}            # symbol -> (reason, timestamp)

        # Live LTP cache
        self.current_ltp = {}                    # symbol -> latest ltp

        self.csv_path = "paper_trades.csv"
        self._load_realized_history()
        self._stop_summary = Event()
        self.summary_thread = None

        self.logger.info("PnLModule initialized (per-buy-reason win-rate + 10s table)")

    def start(self):
        self.market_data = self.engine.modules.get('market_data')
        self.state = self.engine.modules.get('state')

        # Subscribe to events
        self.events.subscribe('order_filled', self._on_order_filled)
        self.events.subscribe('on_tick', self._on_tick)          # for unrealized
        self.events.subscribe('buy_signal', self._on_buy_signal) # capture reason

        # Start periodic table
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
        """Capture buy_reason from AFL/Strategy before fill happens"""
        symbol = data.get('symbol') or data.get('subscribed_symbol')
        reason = data.get('buy_reason', 'unknown')
        if symbol:
            self.pending_buy_reasons[symbol] = (reason, time.time())
            self.logger.debug(f"Captured buy_reason for {symbol}: {reason}")

    def _on_order_filled(self, data):
        """Main event — executed price from order book"""
        order_id = data.get('order_id')
        symbol = data.get('scrip')
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
                if time.time() - ts < 10:  # within 10s window
                    reason = r
                del self.pending_buy_reasons[symbol]

            lot = self._get_lot_size(symbol)

            trade = {
                'trade_id': order_id,
                'symbol': symbol,
                'buy_reason': reason,
                'entry_price': float(price),
                'quantity': int(qty),      # number of contracts/lots
                'lot_size': lot,
                'entry_time': fill_time,
                'status': 'open'
            }
            self.open_trades[order_id] = trade
            self.logger.info(f"PnL → OPEN TRADE | {symbol} | Reason: {reason} | Entry: {price:.2f} | Qty: {qty} | Lot: {lot}")

        elif side == 'sell':
            if order_id in self.open_trades or any(t['symbol'] == symbol for t in self.open_trades.values()):
                # Find open trade for this symbol (last one)
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

                        # Update per-reason stats
                        r = trade['buy_reason']
                        self.per_reason[r]['trades'] += 1
                        self.per_reason[r]['total_pnl'] += realized_pnl
                        if realized_pnl > 0:
                            self.per_reason[r]['wins'] += 1
                        else:
                            self.per_reason[r]['losses'] += 1

                        self._append_to_csv(trade)
                        self.logger.info(f"PnL → CLOSED | {symbol} | Reason: {r} | PnL: ₹{realized_pnl:,.2f} | Win? {realized_pnl > 0}")
                        break

    def _on_tick(self, data):
        """Update unrealized from live LTP"""
        symbol = data.get('symbol') or data.get('scrip')
        ltp = data.get('ltp') or data.get('close')
        if symbol and ltp is not None:
            self.current_ltp[symbol] = float(ltp)

    def _get_lot_size(self, symbol: str) -> int:
        """Safe lot lookup (works with your BSEOptions master)"""
        if self.market_data:
            # Try common places your MarketData stores it
            if hasattr(self.market_data, 'lot_sizes') and symbol in self.market_data.lot_sizes:
                return self.market_data.lot_sizes[symbol]
            if hasattr(self.market_data, 'quotes') and symbol in self.market_data.quotes:
                q = self.market_data.quotes[symbol]
                if 'lot' in q:
                    return int(q['lot'])
        return 10  # SENSEX default — safe fallback

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

    def _summary_loop(self):
        """10-second rich console table"""
        while not self._stop_summary.is_set():
            self._print_pnl_table()
            self._stop_summary.wait(10)

    def _print_pnl_table(self):
        live_pnl = self.get_total_live_pnl()
        unreal = self._calculate_unrealized()
        realized = live_pnl - unreal
        open_count = len(self.open_trades)

        print("\n" + "="*100)
        print(f"🔥 MoNo PnL LIVE @ {datetime.now().strftime('%H:%M:%S')} | "
              f"Total: ₹{live_pnl:,.2f} | Realized: ₹{realized:,.2f} | Unrealized: ₹{unreal:,.2f} | Open: {open_count}")
        print("="*100)

        # Open trades table
        if self.open_trades:
            print("OPEN TRADES")
            print(f"{'Symbol':<15} {'Reason':<20} {'Entry':<8} {'Curr LTP':<8} {'Qty':<4} {'Lot':<4} {'Unreal PnL':<12} {'%':<6}")
            print("-"*90)
            for t in self.open_trades.values():
                ltp = self.current_ltp.get(t['symbol'], 0)
                unreal = (ltp - t['entry_price']) * t['lot_size'] * t['quantity'] if ltp else 0
                pct = ((ltp - t['entry_price']) / t['entry_price'] * 100) if t['entry_price'] else 0
                print(f"{t['symbol']:<15} {t['buy_reason']:<20} {t['entry_price']:<8.2f} "
                      f"{ltp:<8.2f} {t['quantity']:<4} {t['lot_size']:<4} "
                      f"₹{unreal:,.0f} {'+' if unreal>=0 else ''}{pct:6.1f}%")

        # Per-reason summary (closed trades)
        if self.per_reason:
            print("\nPER BUY-REASON PERFORMANCE (Closed Trades)")
            print(f"{'Reason':<25} {'Trades':<6} {'Wins':<5} {'Win%':<6} {'Total PnL':<12}")
            print("-"*60)
            for reason, stats in self.per_reason.items():
                winrate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] else 0
                print(f"{reason:<25} {stats['trades']:<6} {stats['wins']:<5} "
                      f"{winrate:5.1f}%  ₹{stats['total_pnl']:,.0f}")

        print("="*100 + "\n")

    def _load_realized_history(self):
        if os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['realized_pnl'] = float(row['realized_pnl'])
                    self.realized_history.append(row)
                    r = row['buy_reason']
                    self.per_reason[r]['trades'] += 1
                    self.per_reason[r]['total_pnl'] += row['realized_pnl']
                    if row['realized_pnl'] > 0:
                        self.per_reason[r]['wins'] += 1
                    else:
                        self.per_reason[r]['losses'] += 1
            self.logger.info(f"PnL loaded {len(self.realized_history)} historical trades from CSV")

    def _append_to_csv(self, trade):
        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'trade_id', 'symbol', 'buy_reason', 'entry_price', 'exit_price',
                'quantity', 'lot_size', 'entry_time', 'exit_time', 'realized_pnl'
            ])
            if not file_exists:
                writer.writeheader()
            row = {
                'trade_id': trade['trade_id'],
                'symbol': trade['symbol'],
                'buy_reason': trade['buy_reason'],
                'entry_price': trade['entry_price'],
                'exit_price': trade.get('exit_price'),
                'quantity': trade['quantity'],
                'lot_size': trade['lot_size'],
                'entry_time': trade['entry_time'],
                'exit_time': trade.get('exit_time'),
                'realized_pnl': trade.get('realized_pnl', 0)
            }
            writer.writerow(row)