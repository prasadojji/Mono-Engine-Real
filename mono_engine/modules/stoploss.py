# mono_engine/modules/stoploss.py
"""
StopLoss & Trade Management Engine
- Exact conversion of your AFL IN-POSITION logic (no skips)
- Works identically in live (real/paper) and historical replay
- Independent, event-driven, publishes 'exit_signal'
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

        # Per-symbol monitoring state (exact AFL variables)
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

        # For ATR(14) calculation on 1-min bars
        self.hlc_history = defaultdict(list)  # list of (high, low, close)

        self.params = self.engine.config.get('stoploss', {}).get('default', {})
        self.atr_period = 14
        self.atr_mult_trail = self.params.get('ATRMult_Trail', 2.0)

        self.logger.info("StoplossModule initialized (AFL logic loaded)")

    def start(self):
        self.events.subscribe('trade_entered', self._on_trade_entered)
        self.events.subscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.logger.info("StoplossModule started — monitoring for exits (fixed + trailing + streak + 10% protect)")

    def stop(self):
        self.events.unsubscribe('trade_entered', self._on_trade_entered)
        self.events.unsubscribe('1min_bar_closed', self._on_1min_bar_closed)
        self.logger.info("StoplossModule stopped")

    def _get_config(self, key, default):
        return self.engine.config.get('stoploss', {}).get('default', {}).get(key, default)

    def _on_trade_entered(self, data):
        """Called when StateModule confirms a buy fill"""
        symbol = data['symbol']
        entry_price = data['entry_price']

        self.monitor[symbol]['fixed_entry'] = entry_price
        self.monitor[symbol]['max_profit'] = 0.0
        self.monitor[symbol]['breakeven_flag'] = 0
        self.monitor[symbol]['profit_lock_flag'] = 0
        self.monitor[symbol]['trail_start_flag'] = 0
        self.monitor[symbol]['trail_stop'] = 0.0
        self.monitor[symbol]['bars_breached'] = 0
        self.monitor[symbol]['consecutive_streak'] = 0

        self.hlc_history[symbol].clear()  # fresh history for new trade

        self.logger.info(f"Stoploss STARTED monitoring {symbol} @ entry {entry_price}")

    def _on_1min_bar_closed(self, data):
        """Exact AFL IN-POSITION logic — runs on every closed 1-min bar"""
        symbol = data['symbol']
        bar = data['bar']  # {'ts', 'open', 'high', 'low', 'close', 'volume'}

        if not self.engine.modules['state'].is_in_trade(symbol):
            return

        state = self.monitor[symbol]
        if state['fixed_entry'] <= 0:
            return

        current_high = float(bar['high'])
        current_close = float(bar['close'])
        entry = state['fixed_entry']

        # === 1. Update MaxProfit & Flags (exact AFL) ===
        cur_profit = (current_high - entry) / entry * 100 if entry > 0 else 0.0
        state['max_profit'] = max(state['max_profit'], cur_profit)

        if state['max_profit'] >= 2 and state['breakeven_flag'] == 0:
            state['breakeven_flag'] = 1
        if state['max_profit'] >= 5 and state['profit_lock_flag'] == 0:
            state['profit_lock_flag'] = 1
        if state['max_profit'] >= 8 and state['trail_start_flag'] == 0:
            state['trail_start_flag'] = 1

        # === 2. Calculate StopLossCurrent (exact AFL) ===
        if state['profit_lock_flag']:
            sl_mult = 1.02
        elif state['breakeven_flag']:
            sl_mult = 1.00
        else:
            sl_mult = 0.98
        stop_loss_current = entry * sl_mult

        # === 3. Trailing Stop (exact AFL) ===
        if state['trail_start_flag']:
            atr = self._compute_atr(symbol, bar)
            candidate = current_high - atr * self.atr_mult_trail
            state['trail_stop'] = max(max(state['trail_stop'], candidate), stop_loss_current)

        effective_stop = state['trail_stop'] if state['trail_start_flag'] else stop_loss_current

        # === 4. Breach & Streak Logic (exact AFL) ===
        if current_close < effective_stop and state['trail_start_flag'] == 1:
            if state['breach_flag'] == 0:
                state['breach_flag'] = 1
            state['bars_breached'] += 1
            state['consecutive_streak'] += 1
        elif current_close < effective_stop:
            state['consecutive_streak'] = 0
        else:
            state['consecutive_streak'] = 0

        # === 5. SELL LOGIC — EXACT 3 conditions from AFL ===
        profit10 = entry * 1.10
        req_streak = state['required_streak']

        cond1 = (current_close < effective_stop) and (state['trail_start_flag'] == 0)
        cond2 = (state['trail_start_flag'] == 1) and (current_close < effective_stop) and (state['consecutive_streak'] >= req_streak)
        cond3 = (state['trail_start_flag'] == 1) and (state['max_profit'] > 10) and (current_close < profit10)

        if cond1 or cond2 or cond3:
            reason = "fixed_sl" if cond1 else "streak_breach" if cond2 else "profit_protect_10pct"
            exit_price = current_close  # exact AFL: TradeExitPrice = currentMinClose

            self.events.publish('exit_signal', {
                'symbol': symbol,
                'exit_price': exit_price,
                'reason': reason,
                'time': bar['ts'],
                'quantity': self.engine.modules['state'].get_entry_details(symbol).quantity
            })

            self.logger.info(f"🚨 STOPLOSS TRIGGERED SELL {symbol} @ {exit_price:.2f} | Reason: {reason} | MaxProfit: {state['max_profit']:.1f}%")

            self._reset_monitor(symbol)

    def _compute_atr(self, symbol, current_bar):
        """Running ATR(14) on 1-min bars"""
        h, l, c = current_bar['high'], current_bar['low'], current_bar['close']
        self.hlc_history[symbol].append((float(h), float(l), float(c)))
        if len(self.hlc_history[symbol]) > 50:
            self.hlc_history[symbol].pop(0)

        if len(self.hlc_history[symbol]) < self.atr_period + 1:
            return 0.0  # not enough data yet

        highs = np.array([x[0] for x in self.hlc_history[symbol]])
        lows = np.array([x[1] for x in self.hlc_history[symbol]])
        closes = np.array([x[2] for x in self.hlc_history[symbol]])

        atr_series = talib.ATR(highs, lows, closes, timeperiod=self.atr_period)
        return float(atr_series[-1])

    def _reset_monitor(self, symbol):
        """Exact AFL reset on exit"""
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