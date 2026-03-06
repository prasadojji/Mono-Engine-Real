"""
StopLoss & Trade Management Engine
- Exact AFL logic with trailing stops and streak protection
- Works in paper, real, and historical
- Backup start for paper mode
"""

import logging
from collections import defaultdict
import numpy as np
import talib
from datetime import datetime
from .base import BaseModule


class StoplossModule(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.monitor = defaultdict(lambda: {
            'fixed_entry': 0.0,
            'current_high': 0.0,
            'max_profit': 0.0,
            'breakeven_flag': 0,
            'profit_lock_flag': 0,
            'trail_start_flag': 0,
            'trail_stop': 0.0,
            'breach_flag': 0,
            'bars_breached': 0,
            'consecutive_streak': 0,
            'consecutive_ticks': 0,
            'required_streak': self._get_config('required_streak', 3),
        })
        self.hlc_history = defaultdict(list)
        self.post_exit_monitor = defaultdict(lambda: {
            'exit_time': None,
            'exit_price': 0.0,
            'symbol': '',
            'monitoring_active': False,
            'monitoring_end_time': None,
            'price_history': [],
            'max_price_after_exit': 0.0,
            'min_price_after_exit': float('inf'),
            'recovered_to_entry': False,
            'recovered_above_entry': False,
            'monitoring_duration_minutes': self._get_config('post_exit_monitoring_minutes', 60),
        })
        self.params = self.engine.config.get('stoploss_params', {})
        self.atr_period = 14
        self.atr_mult_trail = self.params.get('ATRMult_Trail', 2.0)

        # Configurable SL multipliers and profit thresholds
        self.initial_sl_mult = self.params.get('initial_sl_mult', 0.98)
        self.breakeven_mult = self.params.get('breakeven_mult', 1.00)
        self.profit_lock_mult = self.params.get('profit_lock_mult', 1.02)
        self.breakeven_threshold = self.params.get('breakeven_threshold', 2)
        self.profit_lock_threshold = self.params.get('profit_lock_threshold', 5)
        self.trail_start_threshold = self.params.get('trail_start_threshold', 8)
        self.profit_protect_threshold = self.params.get('profit_protect_threshold', 10)
        self.logger.info("StoplossModule initialized (AFL logic loaded)")

    def start(self):
        self.events.subscribe('trade_entered', self._on_trade_entered)
        self.events.subscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.events.subscribe('on_tick', self._on_tick)  # For real-time checking
        self.events.subscribe('order_filled', self._on_order_filled_backup)  # backup for paper
        self.events.subscribe('trade_exited', self._on_trade_exited)  # For post-exit monitoring
        self.logger.info("StoplossModule started — monitoring AFL stoploss logic")

    def stop(self):
        self.events.unsubscribe('trade_entered', self._on_trade_entered)
        self.events.unsubscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.events.unsubscribe('on_tick', self._on_tick)
        self.events.unsubscribe('order_filled', self._on_order_filled_backup)
        self.logger.info("StoplossModule stopped")

    def _get_config(self, key, default):
        return self.engine.config.get('stoploss_params', {}).get(key, default)

    def _on_trade_entered(self, data):
        symbol = data['symbol']
        entry_price = data['entry_price']
        self._start_monitoring(symbol, entry_price)

    def _on_order_filled_backup(self, data):
        """Backup for paper mode"""
        if data.get('order_type') != 'buy':
            return
        symbol = data.get('scrip') or data.get('symbol')
        if symbol:
            self._start_monitoring(symbol, data.get('price'))

    def _start_monitoring(self, symbol, entry_price):
        self.monitor[symbol]['fixed_entry'] = entry_price
        self.monitor[symbol]['current_high'] = entry_price
        self.monitor[symbol]['max_profit'] = 0.0
        self.monitor[symbol]['breakeven_flag'] = 0
        self.monitor[symbol]['profit_lock_flag'] = 0
        self.monitor[symbol]['trail_start_flag'] = 0
        self.monitor[symbol]['trail_stop'] = 0.0
        self.monitor[symbol]['bars_breached'] = 0
        self.monitor[symbol]['consecutive_streak'] = 0
        self.monitor[symbol]['consecutive_ticks'] = 0
        self.hlc_history[symbol].clear()
        self.logger.info(f"Stoploss STARTED monitoring {symbol} @ entry {entry_price}")

    def _on_1min_bar_closed(self, data):
        symbol = data['symbol']
        bar = data['bar']

        if not self.engine.modules['state'].is_in_trade(symbol):
            return

        monitor_state = self.monitor[symbol]
        if monitor_state['fixed_entry'] <= 0:
            return

        current_high = float(bar['high'])
        current_close = float(bar['close'])
        entry = monitor_state['fixed_entry']

        # === Your exact AFL logic with configurable parameters ===
        cur_profit = (current_high - entry) / entry * 100 if entry > 0 else 0.0
        monitor_state['max_profit'] = max(monitor_state['max_profit'], cur_profit)
        if monitor_state['max_profit'] >= self.breakeven_threshold and monitor_state['breakeven_flag'] == 0:
            monitor_state['breakeven_flag'] = 1
        if monitor_state['max_profit'] >= self.profit_lock_threshold and monitor_state['profit_lock_flag'] == 0:
            monitor_state['profit_lock_flag'] = 1
        if monitor_state['max_profit'] >= self.trail_start_threshold and monitor_state['trail_start_flag'] == 0:
            monitor_state['trail_start_flag'] = 1

        if monitor_state['profit_lock_flag']:
            sl_mult = self.profit_lock_mult
        elif monitor_state['breakeven_flag']:
            sl_mult = self.breakeven_mult
        else:
            sl_mult = self.initial_sl_mult
        stop_loss_current = entry * sl_mult

        if monitor_state['trail_start_flag']:
            # More conservative trailing stop: never allow more than 2% loss
            atr = self._compute_atr(symbol, bar)
            trail_distance = min(atr * self.atr_mult_trail, current_high * 0.05)  # Max 5% trail
            candidate = max(current_high - trail_distance, entry * 1.02)  # Never below 2% profit
            monitor_state['trail_stop'] = max(monitor_state['trail_stop'], candidate)

        effective_stop = monitor_state['trail_stop'] if monitor_state['trail_start_flag'] else stop_loss_current

        if current_close < effective_stop and monitor_state['trail_start_flag'] == 1:
            if monitor_state['breach_flag'] == 0:
                monitor_state['breach_flag'] = 1
            monitor_state['bars_breached'] += 1
            monitor_state['consecutive_streak'] += 1
        elif current_close < effective_stop:
            monitor_state['consecutive_streak'] = 0
        else:
            monitor_state['consecutive_streak'] = 0

        profit_protect_level = entry * (1 + self.profit_protect_threshold / 100)
        req_streak = monitor_state['required_streak']

        # Determine current stage for exit reason
        if monitor_state['trail_start_flag'] == 0:
            if monitor_state['profit_lock_flag'] == 0 and monitor_state['breakeven_flag'] == 0:
                current_stage = "initial"
            elif monitor_state['breakeven_flag'] == 1 and monitor_state['profit_lock_flag'] == 0:
                current_stage = "breakeven"
            else:
                current_stage = "profit_lock"
        else:
            current_stage = "trailing"

        cond1 = (current_close < effective_stop) and (monitor_state['trail_start_flag'] == 0)
        cond2 = (monitor_state['trail_start_flag'] == 1) and (current_close < effective_stop) and (monitor_state['consecutive_streak'] >= req_streak)
        cond3 = (monitor_state['trail_start_flag'] == 1) and (monitor_state['max_profit'] > self.profit_protect_threshold) and (current_close < profit_protect_level)

        if cond1 or cond2 or cond3:
            # Enhanced exit reasons tied to stages
            if cond1:
                if current_stage == "initial":
                    reason = "initial_sl_hit"
                elif current_stage == "breakeven":
                    reason = "breakeven_sl_hit"
                else:  # profit_lock
                    reason = "profit_lock_sl_hit"
            elif cond2:
                reason = "trailing_sl_streak_breach"
            else:  # cond3
                reason = "trailing_sl_profit_protect"

            exit_price = current_close
            exit_payload = {
                'symbol': symbol,
                'exit_price': exit_price,
                'reason': reason,
                'time': bar['ts'],
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity,
                'current_sl_level': effective_stop,
                'max_profit_pct': monitor_state['max_profit'],
                'streak_count': monitor_state['consecutive_streak'],
                'stage': current_stage
            }
            self.events.publish('exit_signal', exit_payload)
            self.logger.info(f"🚨 STOPLOSS TRIGGERED SELL {symbol} @ {exit_price:.2f} | Reason: {reason} | Stage: {current_stage} | SL: {effective_stop:.2f} | MaxProfit: {monitor_state['max_profit']:.1f}% | Streak: {monitor_state['consecutive_streak']}")
            self._reset_monitor(symbol)

    def _on_tick(self, data):
        symbol = data['symbol']
        ltp = float(data['ltp'])
        current_time = datetime.now()

        # Update post-exit monitoring for this symbol (regardless of trade status)
        self._update_post_exit_monitoring(symbol, ltp, current_time)

        if not self.engine.modules['state'].is_in_trade(symbol):
            return

        monitor_state = self.monitor[symbol]
        if monitor_state['fixed_entry'] <= 0:
            return

        entry = monitor_state['fixed_entry']

        # Update current high from ticks
        monitor_state['current_high'] = max(monitor_state['current_high'], ltp)

        # Update max profit
        cur_profit = (monitor_state['current_high'] - entry) / entry * 100 if entry > 0 else 0.0
        monitor_state['max_profit'] = max(monitor_state['max_profit'], cur_profit)

        # Update flags
        if monitor_state['max_profit'] >= self.breakeven_threshold and monitor_state['breakeven_flag'] == 0:
            monitor_state['breakeven_flag'] = 1
        if monitor_state['max_profit'] >= self.profit_lock_threshold and monitor_state['profit_lock_flag'] == 0:
            monitor_state['profit_lock_flag'] = 1
        if monitor_state['max_profit'] >= self.trail_start_threshold and monitor_state['trail_start_flag'] == 0:
            monitor_state['trail_start_flag'] = 1

        # Calculate stop levels
        if monitor_state['profit_lock_flag']:
            sl_mult = self.profit_lock_mult
        elif monitor_state['breakeven_flag']:
            sl_mult = self.breakeven_mult
        else:
            sl_mult = self.initial_sl_mult
        stop_loss_current = entry * sl_mult

        effective_stop = monitor_state['trail_stop'] if monitor_state['trail_start_flag'] else stop_loss_current

        # Update tick streak
        if ltp < effective_stop:
            monitor_state['consecutive_ticks'] += 1
        else:
            monitor_state['consecutive_ticks'] = 0

        # Check exit conditions with configurable parameters
        req_streak = monitor_state['required_streak']
        profit_protect_level = entry * (1 + self.profit_protect_threshold / 100)

        # Determine current stage for exit reason
        if monitor_state['trail_start_flag'] == 0:
            if monitor_state['profit_lock_flag'] == 0 and monitor_state['breakeven_flag'] == 0:
                current_stage = "initial"
            elif monitor_state['breakeven_flag'] == 1 and monitor_state['profit_lock_flag'] == 0:
                current_stage = "breakeven"
            else:
                current_stage = "profit_lock"
        else:
            current_stage = "trailing"

        cond1 = (ltp < effective_stop) and (monitor_state['trail_start_flag'] == 0)
        cond2 = (monitor_state['trail_start_flag'] == 1) and (ltp < effective_stop) and (monitor_state['consecutive_ticks'] >= req_streak)
        cond3 = (monitor_state['trail_start_flag'] == 1) and (monitor_state['max_profit'] > self.profit_protect_threshold) and (ltp < profit_protect_level)

        # Strict tick-based stop loss: trigger immediately if LTP drops below effective stop
        strict_stop_trigger = (ltp < effective_stop)

        if cond1 or cond2 or cond3 or strict_stop_trigger:
            # Enhanced exit reasons tied to stages
            if cond1:
                if current_stage == "initial":
                    reason = "initial_sl_hit"
                elif current_stage == "breakeven":
                    reason = "breakeven_sl_hit"
                else:  # profit_lock
                    reason = "profit_lock_sl_hit"
            elif cond2:
                reason = "trailing_sl_streak_breach"
            elif cond3:
                reason = "trailing_sl_profit_protect"
            else:  # strict_stop_trigger
                reason = "strict_tick_sl"

            exit_price = ltp  # Use current LTP for immediate execution
            exit_payload = {
                'symbol': symbol,
                'exit_price': exit_price,
                'reason': reason,
                'time': datetime.now(),
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity,
                'current_sl_level': effective_stop,
                'max_profit_pct': monitor_state['max_profit'],
                'streak_count': monitor_state['consecutive_ticks'],
                'stage': current_stage
            }
            self.events.publish('exit_signal', exit_payload)
            self.logger.info(f"🚨 IMMEDIATE STOPLOSS SELL {symbol} @ {exit_price:.2f} | Reason: {reason} | Stage: {current_stage} | SL: {effective_stop:.2f} | MaxProfit: {monitor_state['max_profit']:.1f}% | Streak: {monitor_state['consecutive_ticks']}")
            self._reset_monitor(symbol)

    def _on_trade_exited(self, data):
        """Handle trade exit and start post-exit monitoring"""
        symbol = data.get('symbol')
        exit_price = data.get('exit_price')
        exit_time = data.get('exit_time', datetime.now())

        if not symbol or not exit_price:
            return

        # Get entry price from state module
        entry_details = self.engine.modules['state'].get_entry_details(symbol)
        if entry_details and hasattr(entry_details, 'entry_price'):
            entry_price = entry_details.entry_price
            self._start_post_exit_monitoring(symbol, exit_price, exit_time, entry_price)
        else:
            self.logger.warning(f"Could not get entry price for {symbol} - skipping post-exit monitoring")

    def _compute_atr(self, symbol, current_bar):
        h, l, c = current_bar['high'], current_bar['low'], current_bar['close']
        self.hlc_history[symbol].append((float(h), float(l), float(c)))
        if len(self.hlc_history[symbol]) > 50:
            self.hlc_history[symbol].pop(0)
        if len(self.hlc_history[symbol]) < self.atr_period + 1:
            return 0.0
        highs = np.array([x[0] for x in self.hlc_history[symbol]])
        lows = np.array([x[1] for x in self.hlc_history[symbol]])
        closes = np.array([x[2] for x in self.hlc_history[symbol]])
        atr_series = talib.ATR(highs, lows, closes, timeperiod=self.atr_period)
        return float(atr_series[-1])

    def _reset_monitor(self, symbol):
        self.monitor[symbol] = {
            'fixed_entry': 0.0,
            'current_high': 0.0,
            'max_profit': 0.0,
            'breakeven_flag': 0,
            'profit_lock_flag': 0,
            'trail_start_flag': 0,
            'trail_stop': 0.0,
            'breach_flag': 0,
            'bars_breached': 0,
            'consecutive_streak': 0,
            'consecutive_ticks': 0,
            'required_streak': self._get_config('required_streak', 3),
        }
        self.hlc_history[symbol].clear()

    def _start_post_exit_monitoring(self, symbol, exit_price, exit_time, entry_price):
        """Start monitoring price movement after stoploss exit"""
        from datetime import timedelta

        monitor_key = f"{symbol}_{exit_time.strftime('%Y%m%d_%H%M%S')}"

        self.post_exit_monitor[monitor_key] = {
            'exit_time': exit_time,
            'exit_price': exit_price,
            'entry_price': entry_price,
            'symbol': symbol,
            'monitoring_active': True,
            'monitoring_end_time': exit_time + timedelta(minutes=self._get_config('post_exit_monitoring_minutes', 60)),
            'price_history': [],
            'max_price_after_exit': exit_price,
            'min_price_after_exit': exit_price,
            'recovered_to_entry': False,
            'recovered_above_entry': False,
            'monitoring_duration_minutes': self._get_config('post_exit_monitoring_minutes', 60),
        }

        self.logger.info(f"📊 Started post-exit monitoring for {symbol} | Exit: {exit_price:.2f} | Entry: {entry_price:.2f} | Monitor until: {self.post_exit_monitor[monitor_key]['monitoring_end_time']}")

    def _update_post_exit_monitoring(self, symbol, current_price, current_time):
        """Update post-exit monitoring with current price data"""
        # Find active monitoring sessions for this symbol
        active_sessions = [k for k, v in self.post_exit_monitor.items()
                          if v['symbol'] == symbol and v['monitoring_active']]

        for session_key in active_sessions:
            session = self.post_exit_monitor[session_key]

            # Check if monitoring period has ended
            if current_time > session['monitoring_end_time']:
                session['monitoring_active'] = False
                self._finalize_post_exit_analysis(session_key)
                continue

            # Update price tracking
            session['price_history'].append({
                'time': current_time,
                'price': current_price
            })

            session['max_price_after_exit'] = max(session['max_price_after_exit'], current_price)
            session['min_price_after_exit'] = min(session['min_price_after_exit'], current_price)

            # Check recovery conditions
            if not session['recovered_to_entry'] and current_price >= session['entry_price']:
                session['recovered_to_entry'] = True
                self.logger.info(f"🎯 {symbol} recovered to entry price {session['entry_price']:.2f} after stoploss exit")

            if not session['recovered_above_entry'] and current_price > session['entry_price']:
                session['recovered_above_entry'] = True
                self.logger.info(f"🚀 {symbol} recovered ABOVE entry price {session['entry_price']:.2f} after stoploss exit")

    def _finalize_post_exit_analysis(self, session_key):
        """Finalize post-exit analysis and store results"""
        session = self.post_exit_monitor[session_key]

        # Calculate recovery metrics
        recovery_analysis = {
            'symbol': session['symbol'],
            'exit_time': session['exit_time'],
            'exit_price': session['exit_price'],
            'entry_price': session['entry_price'],
            'max_price_after_exit': session['max_price_after_exit'],
            'min_price_after_exit': session['min_price_after_exit'],
            'recovered_to_entry': session['recovered_to_entry'],
            'recovered_above_entry': session['recovered_above_entry'],
            'price_range_after_exit': session['max_price_after_exit'] - session['min_price_after_exit'],
            'monitoring_duration_minutes': session['monitoring_duration_minutes'],
            'price_history_count': len(session['price_history']),
        }

        # Store in database
        self._store_post_exit_analysis(recovery_analysis)

        self.logger.info(f"📈 Post-exit analysis complete for {session['symbol']}: "
                        f"Max: {session['max_price_after_exit']:.2f}, "
                        f"Min: {session['min_price_after_exit']:.2f}, "
                        f"Recovered: {session['recovered_to_entry']}")

    def _store_post_exit_analysis(self, analysis_data):
        """Store post-exit analysis data in database"""
        try:
            import sqlite3
            db_path = 'mono_engine_data.db'

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Create table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS post_exit_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        exit_time DATETIME,
                        exit_price REAL,
                        entry_price REAL,
                        max_price_after_exit REAL,
                        min_price_after_exit REAL,
                        recovered_to_entry BOOLEAN,
                        recovered_above_entry BOOLEAN,
                        price_range_after_exit REAL,
                        monitoring_duration_minutes INTEGER,
                        price_history_count INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Insert analysis data
                cursor.execute('''
                    INSERT INTO post_exit_analysis
                    (symbol, exit_time, exit_price, entry_price, max_price_after_exit,
                     min_price_after_exit, recovered_to_entry, recovered_above_entry,
                     price_range_after_exit, monitoring_duration_minutes, price_history_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analysis_data['symbol'],
                    analysis_data['exit_time'],
                    analysis_data['exit_price'],
                    analysis_data['entry_price'],
                    analysis_data['max_price_after_exit'],
                    analysis_data['min_price_after_exit'],
                    analysis_data['recovered_to_entry'],
                    analysis_data['recovered_above_entry'],
                    analysis_data['price_range_after_exit'],
                    analysis_data['monitoring_duration_minutes'],
                    analysis_data['price_history_count']
                ))

                conn.commit()
                self.logger.debug(f"Stored post-exit analysis for {analysis_data['symbol']}")

        except Exception as e:
            self.logger.error(f"Failed to store post-exit analysis: {e}")

    def get_post_exit_analysis(self, symbol=None, days_back=30):
        """Get post-exit analysis data for analysis"""
        try:
            import sqlite3
            from datetime import datetime, timedelta

            db_path = 'mono_engine_data.db'

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get analysis data
                query = '''
                    SELECT * FROM post_exit_analysis
                    WHERE exit_time >= ?
                '''
                params = [(datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d %H:%M:%S')]

                if symbol:
                    query += ' AND symbol = ?'
                    params.append(symbol)

                query += ' ORDER BY exit_time DESC'

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Convert to dict format
                columns = [desc[0] for desc in cursor.description]
                analysis_data = [dict(zip(columns, row)) for row in rows]

                return analysis_data

        except Exception as e:
            self.logger.error(f"Failed to get post-exit analysis: {e}")
            return []
