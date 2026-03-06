"""
2% Profit Target Strategy
- Take minimum 2% profit on every trade
- Trail from highest price if profit exceeds 2%
- Exit if price drops 2% below highest achieved price
- Works in paper, real, and historical modes
"""

import logging
from collections import defaultdict
from datetime import datetime
from .base import BaseModule


class Stoploss2PercentModule(BaseModule):
    """
    2% Profit Target Strategy Module
    - No initial stop-loss, focus only on profit-taking
    - Exit at 2% profit minimum, trail beyond that
    - Exit if drops 2% from highest price reached
    """

    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)

        # Simplified monitoring - only track profit targets
        self.monitor = defaultdict(lambda: {
            'entry_price': 0.0,
            'highest_price': 0.0,
            'max_profit_pct': 0.0,
            'target_achieved': False,
            'trail_level': 0.0,
        })

        # Post-exit monitoring (same as original)
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

        # Strategy parameters
        self.profit_target_pct = 2.0  # Minimum 2% profit
        self.trail_buffer_pct = 2.0   # Exit if drops 2% from high

        self.logger.info("Stoploss2PercentModule initialized (2% profit target strategy)")

    def start(self):
        self.events.subscribe('trade_entered', self._on_trade_entered)
        self.events.subscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.events.subscribe('on_tick', self._on_tick)
        self.events.subscribe('order_filled', self._on_order_filled_backup)
        self.events.subscribe('trade_exited', self._on_trade_exited)
        self.logger.info("Stoploss2PercentModule started — monitoring 2% profit targets")

    def stop(self):
        self.events.unsubscribe('trade_entered', self._on_trade_entered)
        self.events.unsubscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.events.unsubscribe('on_tick', self._on_tick)
        self.events.unsubscribe('order_filled', self._on_order_filled_backup)
        self.events.unsubscribe('trade_exited', self._on_trade_exited)
        self.logger.info("Stoploss2PercentModule stopped")

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
        self.monitor[symbol]['entry_price'] = entry_price
        self.monitor[symbol]['highest_price'] = entry_price
        self.monitor[symbol]['max_profit_pct'] = 0.0
        self.monitor[symbol]['target_achieved'] = False
        self.monitor[symbol]['trail_level'] = 0.0
        self.logger.info(f"🎯 2% STRATEGY STARTED monitoring {symbol} @ entry {entry_price}")

    def _on_1min_bar_closed(self, data):
        symbol = data['symbol']
        bar = data['bar']

        if not self.engine.modules['state'].is_in_trade(symbol):
            return

        monitor_state = self.monitor[symbol]
        if monitor_state['entry_price'] <= 0:
            return

        current_high = float(bar['high'])
        current_close = float(bar['close'])
        entry = monitor_state['entry_price']

        # Update highest price and profit
        previous_highest = monitor_state['highest_price']
        monitor_state['highest_price'] = max(monitor_state['highest_price'], current_high)
        highest = monitor_state['highest_price']
        current_profit_pct = (highest - entry) / entry * 100
        monitor_state['max_profit_pct'] = max(monitor_state['max_profit_pct'], current_profit_pct)

        # Check if 2% target achieved
        if not monitor_state['target_achieved'] and current_profit_pct >= self.profit_target_pct:
            monitor_state['target_achieved'] = True
            monitor_state['trail_level'] = highest * (1 - self.trail_buffer_pct / 100)
            self.logger.info(f"🎯 {symbol} achieved 2% target | High: {highest:.2f} | Trail Level: {monitor_state['trail_level']:.2f}")

        # Update trail level if highest price increased and target already achieved
        elif monitor_state['target_achieved'] and highest > previous_highest:
            monitor_state['trail_level'] = highest * (1 - self.trail_buffer_pct / 100)
            self.logger.debug(f"📈 {symbol} trail updated | New High: {highest:.2f} | New Trail: {monitor_state['trail_level']:.2f}")

        # Check exit condition: price drops below trail level after target achieved
        if monitor_state['target_achieved'] and current_close <= monitor_state['trail_level']:
            exit_price = current_close
            exit_payload = {
                'symbol': symbol,
                'exit_price': exit_price,
                'reason': '2percent_profit_target',
                'time': bar['ts'],
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity,
                'current_sl_level': monitor_state['trail_level'],
                'max_profit_pct': monitor_state['max_profit_pct'],
                'highest_price': monitor_state['highest_price'],
                'entry_price': monitor_state['entry_price']
            }
            self.events.publish('exit_signal', exit_payload)
            self.logger.info(f"💰 2% PROFIT EXIT {symbol} @ {exit_price:.2f} | Reason: 2percent_profit_target | "
                           f"High: {monitor_state['highest_price']:.2f} | MaxProfit: {monitor_state['max_profit_pct']:.1f}% | "
                           f"Trail: {monitor_state['trail_level']:.2f}")
            self._reset_monitor(symbol)

    def _on_tick(self, data):
        symbol = data['symbol']
        ltp = float(data['ltp'])
        current_time = datetime.now()

        # Update post-exit monitoring
        self._update_post_exit_monitoring(symbol, ltp, current_time)

        if not self.engine.modules['state'].is_in_trade(symbol):
            return

        monitor_state = self.monitor[symbol]
        if monitor_state['entry_price'] <= 0:
            return

        entry = monitor_state['entry_price']

        # Update highest price and profit
        previous_highest = monitor_state['highest_price']
        monitor_state['highest_price'] = max(monitor_state['highest_price'], ltp)
        highest = monitor_state['highest_price']
        current_profit_pct = (highest - entry) / entry * 100
        monitor_state['max_profit_pct'] = max(monitor_state['max_profit_pct'], current_profit_pct)

        # Check if 2% target achieved
        if not monitor_state['target_achieved'] and current_profit_pct >= self.profit_target_pct:
            monitor_state['target_achieved'] = True
            monitor_state['trail_level'] = highest * (1 - self.trail_buffer_pct / 100)
            self.logger.info(f"🎯 {symbol} achieved 2% target | High: {highest:.2f} | Trail Level: {monitor_state['trail_level']:.2f}")

        # Update trail level if highest price increased and target already achieved
        elif monitor_state['target_achieved'] and highest > previous_highest:
            monitor_state['trail_level'] = highest * (1 - self.trail_buffer_pct / 100)
            self.logger.debug(f"📈 {symbol} trail updated | New High: {highest:.2f} | New Trail: {monitor_state['trail_level']:.2f}")

        # Check exit condition: price drops below trail level after target achieved
        if monitor_state['target_achieved'] and ltp <= monitor_state['trail_level']:
            exit_price = ltp
            exit_payload = {
                'symbol': symbol,
                'exit_price': exit_price,
                'reason': '2percent_profit_target',
                'time': current_time,
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity,
                'current_sl_level': monitor_state['trail_level'],
                'max_profit_pct': monitor_state['max_profit_pct'],
                'highest_price': monitor_state['highest_price'],
                'entry_price': monitor_state['entry_price']
            }
            self.events.publish('exit_signal', exit_payload)
            self.logger.info(f"💰 2% PROFIT EXIT {symbol} @ {exit_price:.2f} | Reason: 2percent_profit_target | "
                           f"High: {monitor_state['highest_price']:.2f} | MaxProfit: {monitor_state['max_profit_pct']:.1f}% | "
                           f"Trail: {monitor_state['trail_level']:.2f}")
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

    def _reset_monitor(self, symbol):
        self.monitor[symbol] = {
            'entry_price': 0.0,
            'highest_price': 0.0,
            'max_profit_pct': 0.0,
            'target_achieved': False,
            'trail_level': 0.0,
        }

    def _start_post_exit_monitoring(self, symbol, exit_price, exit_time, entry_price):
        """Start monitoring price movement after exit"""
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

        self.logger.info(f"📊 Started post-exit monitoring for {symbol} | Exit: {exit_price:.2f} | Entry: {entry_price:.2f}")

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
                self.logger.info(f"🎯 {symbol} recovered to entry price {session['entry_price']:.2f} after exit")

            if not session['recovered_above_entry'] and current_price > session['entry_price']:
                session['recovered_above_entry'] = True
                self.logger.info(f"🚀 {symbol} recovered ABOVE entry price {session['entry_price']:.2f} after exit")

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
                cursor.execute('''INSERT INTO post_exit_analysis
                    (symbol, exit_time, exit_price, entry_price, max_price_after_exit,
                     min_price_after_exit, recovered_to_entry, recovered_above_entry,
                     price_range_after_exit, monitoring_duration_minutes, price_history_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
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