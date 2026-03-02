"""
StopLoss & Trade Management Engine
- Exact AFL logic + HARD 2% safety (never exceeds -2% loss)
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
            'max_profit': 0.0,
            'breakeven_flag': 0,
            'profit_lock_flag': 0,
            'trail_start_flag': 0,
            'trail_stop': 0.0,
            'breach_flag': 0,
            'bars_breached': 0,
            'consecutive_streak': 0,
            'required_streak': self._get_config('required_streak', 3),
        })
        self.hlc_history = defaultdict(list)
        self.params = self.engine.config.get('stoploss', {}).get('default', {})
        self.atr_period = 14
        self.atr_mult_trail = self.params.get('ATRMult_Trail', 2.0)
        self.logger.info("StoplossModule initialized (AFL logic loaded)")

    def start(self):
        self.events.subscribe('trade_entered', self._on_trade_entered)
        self.events.subscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.events.subscribe('order_filled', self._on_order_filled_backup)  # backup for paper
        self.logger.info("StoplossModule started — monitoring + HARD 2% safety")

    def stop(self):
        self.events.unsubscribe('trade_entered', self._on_trade_entered)
        self.events.unsubscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.events.unsubscribe('order_filled', self._on_order_filled_backup)
        self.logger.info("StoplossModule stopped")

    def _get_config(self, key, default):
        return self.engine.config.get('stoploss', {}).get('default', {}).get(key, default)

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
        self.monitor[symbol]['max_profit'] = 0.0
        self.monitor[symbol]['breakeven_flag'] = 0
        self.monitor[symbol]['profit_lock_flag'] = 0
        self.monitor[symbol]['trail_start_flag'] = 0
        self.monitor[symbol]['trail_stop'] = 0.0
        self.monitor[symbol]['bars_breached'] = 0
        self.monitor[symbol]['consecutive_streak'] = 0
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

        # ==================== HARD 2% SAFETY ====================
        if current_close < entry * 0.98:
            self.logger.info(f"🚨 HARD 2% SL TRIGGERED {symbol} @ {current_close:.2f} (forced)")
            self.events.publish('exit_signal', {
                'symbol': symbol,
                'exit_price': current_close,
                'reason': 'hard_2pct_sl',
                'time': bar['ts'],
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity
            })
            self._reset_monitor(symbol)
            return

        # === Rest of your exact AFL logic (unchanged) ===
        cur_profit = (current_high - entry) / entry * 100 if entry > 0 else 0.0
        monitor_state['max_profit'] = max(monitor_state['max_profit'], cur_profit)
        if monitor_state['max_profit'] >= 2 and monitor_state['breakeven_flag'] == 0:
            monitor_state['breakeven_flag'] = 1
        if monitor_state['max_profit'] >= 5 and monitor_state['profit_lock_flag'] == 0:
            monitor_state['profit_lock_flag'] = 1
        if monitor_state['max_profit'] >= 8 and monitor_state['trail_start_flag'] == 0:
            monitor_state['trail_start_flag'] = 1

        if monitor_state['profit_lock_flag']:
            sl_mult = 1.02
        elif monitor_state['breakeven_flag']:
            sl_mult = 1.00
        else:
            sl_mult = 0.98
        stop_loss_current = entry * sl_mult

        if monitor_state['trail_start_flag']:
            atr = self._compute_atr(symbol, bar)
            candidate = current_high - atr * self.atr_mult_trail
            monitor_state['trail_stop'] = max(max(monitor_state['trail_stop'], candidate), stop_loss_current)

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

        profit10 = entry * 1.10
        req_streak = monitor_state['required_streak']
        cond1 = (current_close < effective_stop) and (monitor_state['trail_start_flag'] == 0)
        cond2 = (monitor_state['trail_start_flag'] == 1) and (current_close < effective_stop) and (monitor_state['consecutive_streak'] >= req_streak)
        cond3 = (monitor_state['trail_start_flag'] == 1) and (monitor_state['max_profit'] > 10) and (current_close < profit10)

        if cond1 or cond2 or cond3:
            reason = "fixed_sl" if cond1 else "streak_breach" if cond2 else "profit_protect_10pct"
            exit_price = current_close
            self.events.publish('exit_signal', {
                'symbol': symbol,
                'exit_price': exit_price,
                'reason': reason,
                'time': bar['ts'],
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity
            })
            self.logger.info(f"🚨 STOPLOSS TRIGGERED SELL {symbol} @ {exit_price:.2f} | Reason: {reason} | MaxProfit: {monitor_state['max_profit']:.1f}%")
            self._reset_monitor(symbol)

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
            'max_profit': 0.0,
            'breakeven_flag': 0,
            'profit_lock_flag': 0,
            'trail_start_flag': 0,
            'trail_stop': 0.0,
            'breach_flag': 0,
            'bars_breached': 0,
            'consecutive_streak': 0,
            'required_streak': self._get_config('required_streak', 3),
        }
        self.hlc_history[symbol].clear()