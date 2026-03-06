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
        self.pending_sell_reasons = {}
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
        # Original trades table (keep for backward compatibility)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                symbol TEXT,
                buy_reason TEXT,
                sell_reason TEXT,
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

        # New enhanced signals table for real-time publishing
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades_signals (
                signal_id TEXT PRIMARY KEY,
                trade_id TEXT,
                symbol TEXT,
                signal_type TEXT,
                signal_reason TEXT,
                signal_price REAL,
                candle_close REAL,
                next_candle_direction INTEGER,
                signal_time TEXT,
                fill_price REAL,
                fill_time TEXT,
                realized_pnl REAL,
                is_live INTEGER,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _update_signal_on_fill(self, trade_id, symbol, signal_type, fill_price, fill_time):
        """Update signal record when order is filled"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Find the most recent signal for this symbol/type that doesn't have fill info
        cursor.execute("""
            SELECT signal_id FROM trades_signals
            WHERE symbol = ? AND signal_type = ? AND fill_price IS NULL
            ORDER BY signal_time DESC
            LIMIT 1
        """, (symbol, signal_type))

        result = cursor.fetchone()
        if result:
            signal_id = result[0]
            # Update the specific signal record
            cursor.execute("""
                UPDATE trades_signals
                SET trade_id = ?, fill_price = ?, fill_time = ?, status = 'filled'
                WHERE signal_id = ?
            """, (trade_id, fill_price, str(fill_time), signal_id))

        conn.commit()
        conn.close()
        self.logger.info("PnL database ready (trades + trades_signals tables created)")

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
        # Use explicit column names to avoid any column ordering issues
        conn.execute('''INSERT OR REPLACE INTO trades
            (trade_id, symbol, buy_reason, sell_reason, entry_price, exit_price,
             quantity, lot_size, entry_time, exit_time, realized_pnl, is_historical,
             buy_date, buy_time, sell_date, sell_time, pnl_rs, symbol_readable)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            trade.get('trade_id'), trade.get('symbol'), trade.get('buy_reason'),
            trade.get('sell_reason', 'unknown'), trade.get('entry_price'), trade.get('exit_price'),
            trade.get('quantity'), trade.get('lot_size'), str(trade.get('entry_time')),
            str(trade.get('exit_time')), trade.get('realized_pnl', 0), 1 if is_historical else 0,
            None, None, None, None,  # buy_date, buy_time, sell_date, sell_time
            trade.get('realized_pnl', 0),  # pnl_rs
            None  # symbol_readable
        ))
        conn.commit()
        conn.close()

    def _store_open_trade(self, trade):
        """Store open trade in database"""
        conn = sqlite3.connect(self.db_path)
        # For open trades, exit_price, exit_time, sell_reason, realized_pnl are NULL/None
        # Make sure we use the correct column order
        conn.execute('''INSERT OR REPLACE INTO trades
            (trade_id, symbol, buy_reason, sell_reason, entry_price, exit_price,
             quantity, lot_size, entry_time, exit_time, realized_pnl, is_historical,
             buy_date, buy_time, sell_date, sell_time, pnl_rs, symbol_readable)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            trade.get('trade_id'), trade.get('symbol'), trade.get('buy_reason'),
            None,  # sell_reason (None for open trades)
            trade.get('entry_price'), None,  # exit_price (None for open trades)
            trade.get('quantity'), trade.get('lot_size'), str(trade.get('entry_time')),
            None,  # exit_time (None for open trades)
            0,  # realized_pnl (0 for open trades)
            0,  # is_historical
            None, None, None, None,  # buy_date, buy_time, sell_date, sell_time
            0,  # pnl_rs
            None  # symbol_readable
        ))
        conn.commit()
        conn.close()

    def start(self):
        self.market_data = self.engine.modules.get('market_data')
        self.state = self.engine.modules.get('state')
        self.events.subscribe('order_filled', self._on_order_filled)
        self.events.subscribe('on_tick', self._on_tick)
        self.events.subscribe('buy_signal', self._on_buy_signal)
        self.events.subscribe('exit_signal', self._on_exit_signal)
        self.events.subscribe('1min_bar_closed', self._on_1min_bar_closed)
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
        self.events.unsubscribe('exit_signal', self._on_exit_signal)
        self.events.unsubscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.logger.info("PnLModule stopped")

    def _on_buy_signal(self, data):
        symbol = data.get('symbol') or data.get('subscribed_symbol')
        reason = data.get('buy_reason', 'unknown')
        price = data.get('price', 0.0)
        quantity = data.get('quantity', 900)

        if symbol:
            self.pending_buy_reasons[symbol] = (reason, time.time())

            # Publish buy signal immediately to DB
            signal_id = f"buy_signal_{symbol}_{int(time.time() * 1000)}"
            self._publish_signal_to_db({
                'signal_id': signal_id,
                'trade_id': None,  # Will be set when filled
                'symbol': symbol,
                'signal_type': 'buy',
                'signal_reason': reason,
                'signal_price': price,
                'candle_close': None,  # Will be updated on next bar
                'next_candle_direction': None,
                'signal_time': datetime.now(),
                'fill_price': None,
                'fill_time': None,
                'realized_pnl': None,
                'is_live': 0 if self.is_historical_run else 1,
                'status': 'signaled'
            })

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

            # Store open trade in database immediately
            try:
                self._store_open_trade(trade)
                self.logger.info(f"✅ Stored open trade {order_id} for {symbol} @ {price:.2f}")
            except Exception as e:
                self.logger.error(f"❌ Failed to store open trade {order_id} in database: {e}")

            # Update buy signal record with trade_id and fill info
            self._update_signal_on_fill(order_id, symbol, 'buy', price, fill_time)

        elif side == 'sell':
            # First check if sell_reason is provided in the order_filled event data (for paper trading)
            sell_reason = data.get('sell_reason', 'unknown')

            # If not provided, check pending_sell_reasons (for real trading)
            if sell_reason == 'unknown' and symbol in self.pending_sell_reasons:
                r, ts = self.pending_sell_reasons[symbol]
                if time.time() - ts < 10:
                    sell_reason = r
                del self.pending_sell_reasons[symbol]

            # Find matching open trade
            matching_trade = None
            for tid, t in list(self.open_trades.items()):
                if t['symbol'] == symbol:
                    matching_trade = (tid, t)
                    break

            if matching_trade:
                tid, trade = matching_trade
                exit_price = float(price)
                realized_pnl = (exit_price - trade['entry_price']) * trade['lot_size'] * trade['quantity']
                trade['exit_price'] = exit_price
                trade['exit_time'] = fill_time
                trade['sell_reason'] = sell_reason
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

                # Store the completed trade in database
                try:
                    self._append_to_db(trade)
                    self.logger.info(f"✅ Stored completed trade {tid} for {symbol}: PnL ₹{realized_pnl:,.0f}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to store trade {tid} in database: {e}")

                # Update sell signal record with fill info
                self._update_signal_on_fill(tid, symbol, 'sell', exit_price, fill_time)
            else:
                self.logger.warning(f"⚠️ No matching open trade found for sell order {order_id} on {symbol}")

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
        print(f"{'Symbol':<25} {'Buy Reason':<20} {'Sell Reason':<15} {'Entry':<10} {'Exit/LTP':<10} {'Shares':<10} {'PnL ₹':<12} {'%':<8} {'Status'}")
        print("-"*130)

        # Closed trades
        for t in self.realized_history:
            sym = self._get_readable_symbol(t['symbol'])
            exit_p = t.get('exit_price', 0)
            pnl = t.get('realized_pnl', 0)
            pct = ((exit_p - t['entry_price']) / t['entry_price'] * 100) if t['entry_price'] else 0
            sell_reason = t.get('sell_reason', 'unknown')
            total_shares = t['quantity'] * t['lot_size']
            print(f"{sym:<25} {t['buy_reason']:<20} {sell_reason:<15} {t['entry_price']:<10.2f} {exit_p:<10.2f} "
                  f"{total_shares:<10} ₹{pnl:,.0f} {pct:6.1f}% Closed")

        # Open trades with live LTP
        for t in list(self.open_trades.values()):
            sym = self._get_readable_symbol(t['symbol'])
            ltp = self.current_ltp.get(t['symbol'], t['entry_price'])
            unreal = (ltp - t['entry_price']) * t['lot_size'] * t['quantity']
            pct = ((ltp - t['entry_price']) / t['entry_price'] * 100) if t['entry_price'] else 0
            total_shares = t['quantity'] * t['lot_size']
            print(f"{sym:<25} {t['buy_reason']:<20} {'-':<15} {t['entry_price']:<10.2f} {ltp:<10.2f} "
                  f"{total_shares:<10} ₹{unreal:,.0f} {pct:6.1f}% Open")

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

    def _publish_signal_to_db(self, signal_data):
        """Publish signal to trades_signals table immediately"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''INSERT OR REPLACE INTO trades_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            signal_data['signal_id'],
            signal_data['trade_id'],
            signal_data['symbol'],
            signal_data['signal_type'],
            signal_data['signal_reason'],
            signal_data['signal_price'],
            signal_data['candle_close'],
            signal_data['next_candle_direction'],
            str(signal_data['signal_time']),
            signal_data['fill_price'],
            str(signal_data['fill_time']) if signal_data['fill_time'] else None,
            signal_data['realized_pnl'],
            signal_data['is_live'],
            signal_data['status']
        ))
        conn.commit()
        conn.close()

    def _on_exit_signal(self, data):
        """Handle exit signals and publish immediately to DB"""
        symbol = data.get('symbol')
        exit_price = data.get('exit_price', 0.0)
        reason = data.get('reason', 'unknown')
        quantity = data.get('quantity', 900)

        if symbol:
            # Store sell reason for when order is filled
            self.pending_sell_reasons[symbol] = (reason, time.time())

            # Find the corresponding buy signal for this symbol
            trade_id = None
            for trade in self.open_trades.values():
                if trade['symbol'] == symbol:
                    trade_id = trade['trade_id']
                    break

            # Publish sell signal immediately to DB
            signal_id = f"sell_signal_{symbol}_{int(time.time() * 1000)}"
            self._publish_signal_to_db({
                'signal_id': signal_id,
                'trade_id': trade_id,
                'symbol': symbol,
                'signal_type': 'sell',
                'signal_reason': reason,
                'signal_price': exit_price,
                'candle_close': None,  # Will be updated on next bar
                'next_candle_direction': None,
                'signal_time': datetime.now(),
                'fill_price': None,
                'fill_time': None,
                'realized_pnl': None,
                'is_live': 0 if self.is_historical_run else 1,
                'status': 'signaled'
            })

    def _on_1min_bar_closed(self, data):
        """Track candle closes and update next candle direction for recent signals"""
        bar = data.get('bar', {})
        symbol = data.get('symbol')
        current_close = float(bar.get('close', 0))

        if not symbol:
            return

        # Update candle_close for signals that don't have it yet
        # and calculate next_candle_direction for signals that have candle_close
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get recent signals for this symbol that need updating
        cursor.execute("""
            SELECT signal_id, candle_close, signal_price
            FROM trades_signals
            WHERE symbol = ? AND (candle_close IS NULL OR next_candle_direction IS NULL)
            ORDER BY signal_time DESC
            LIMIT 10
        """, (symbol,))

        signals_to_update = cursor.fetchall()

        for signal_id, candle_close, signal_price in signals_to_update:
            if candle_close is None:
                # Update candle_close for this signal
                cursor.execute("""
                    UPDATE trades_signals
                    SET candle_close = ?
                    WHERE signal_id = ?
                """, (current_close, signal_id))
            else:
                # Calculate next candle direction (1=up, 0=down)
                next_direction = 1 if current_close > candle_close else 0
                cursor.execute("""
                    UPDATE trades_signals
                    SET next_candle_direction = ?
                    WHERE signal_id = ?
                """, (next_direction, signal_id))

        conn.commit()
        conn.close()
    