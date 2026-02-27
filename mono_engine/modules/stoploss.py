import logging
from collections import defaultdict, deque
import numpy as np  # Assuming numpy is available in the environment

from mono_engine.modules.base import BaseModule

class StopLossState:
    def __init__(self):
        self.entry_price = None
        self.stop_loss = None
        self.high_price = None
        self.breach_count = 0
        self.max_profit = 0.0
        self.trailing_active = False
        self.candle_history = deque(maxlen=50)  # Sufficient for ATR period, e.g., 14 + buffer

def calculate_atr(candles, period=14):
    if len(candles) < period + 1:
        return None
    highs = np.array([c['high'] for c in candles])
    lows = np.array([c['low'] for c in candles])
    closes = np.array([c['close'] for c in candles])
    tr = np.maximum(highs[1:] - lows[1:],
                    np.maximum(np.abs(highs[1:] - closes[:-1]),
                               np.abs(lows[1:] - closes[:-1])))
    atr = np.mean(tr[-period:])  # Simple moving average approximation; can be upgraded to Wilder's
    return atr

class StoplossModule(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.params = self.config.get('stoploss_params', {})
        self.initial_sl_pct = self.params.get('initial_sl_pct', 0.02)
        self.breakeven_pct = self.params.get('breakeven_pct', 0.02)
        self.profit_lock_pct = self.params.get('profit_lock_pct', 0.05)
        self.trail_start_pct = self.params.get('trail_start_pct', 0.08)
        self.atr_period = self.params.get('atr_period', 14)
        self.atr_multiplier = self.params.get('atr_multiplier', 3.0)
        self.breach_base_streak = self.params.get('breach_base_streak', 3)
        self.breach_scale_factor = self.params.get('breach_scale_factor', 0.5)  # e.g., add 0.5 per 1% profit
        self.profit_target_pct = self.params.get('profit_target_pct', 0.10)
        self.quantity = self.params.get('quantity', 900)
        
        self.state = defaultdict(StopLossState)
        
        self.events.subscribe('state_updated', self.on_state_updated)
        self.events.subscribe('on_tick', self.on_tick)
        self.events.subscribe('on_connect', self.on_connect)

    def on_state_updated(self, event):
        symbol = event.get('symbol')
        if not symbol:
            return
        in_trade = event.get('in_trade', False)
        entry_price = event.get('entry_price')
        
        if in_trade and entry_price and not self.state[symbol].entry_price:
            # New position opened
            self.state[symbol].entry_price = entry_price
            self.state[symbol].stop_loss = entry_price * (1 - self.initial_sl_pct)
            self.state[symbol].high_price = entry_price
            self.state[symbol].breach_count = 0
            self.state[symbol].max_profit = 0.0
            self.state[symbol].trailing_active = False
            self.logger.info(f"StoplossModule: Position opened for {symbol} at {entry_price}. Initial SL: {self.state[symbol].stop_loss}")

    def on_tick(self, event):
        symbol = event.get('symbol')
        if not symbol or not self.state[symbol].entry_price:
            return
        
        # Assume event has 'candle' with ohlcv or at least 'close' for current price
        candle = event.get('candle', {})
        current_price = candle.get('close', event.get('ltp'))  # Fallback to ltp if no candle
        
        if not current_price:
            return
        
        # Append candle if available for ATR
        if candle:
            self.state[symbol].candle_history.append(candle)
        
        state = self.state[symbol]
        state.high_price = max(state.high_price, current_price)
        current_profit = (current_price - state.entry_price) / state.entry_price
        state.max_profit = max(state.max_profit, (state.high_price - state.entry_price) / state.entry_price)
        
        # Breakeven
        breakeven_level = state.entry_price * (1 + self.breakeven_pct)
        if current_price > breakeven_level:
            state.stop_loss = max(state.stop_loss, state.entry_price)
        
        # Profit lock at 5%
        profit_lock_level = state.entry_price * (1 + self.profit_lock_pct)
        if current_price > profit_lock_level:
            # Lock in some profit, e.g., set SL to entry + 1% or adjustable
            state.stop_loss = max(state.stop_loss, state.entry_price * (1 + self.profit_lock_pct / 5))  # Example: lock 1/5 of profit
        
        # Start trailing at 8%
        trail_start_level = state.entry_price * (1 + self.trail_start_pct)
        if current_price > trail_start_level:
            state.trailing_active = True
        
        # ATR trailing if active
        if state.trailing_active:
            atr = calculate_atr(state.candle_history, self.atr_period)
            if atr:
                trailing_stop = current_price - atr * self.atr_multiplier
                state.stop_loss = max(state.stop_loss, trailing_stop)
        
        # Check for sell conditions
        reason = None
        
        # Profit target >10%
        if state.max_profit > self.profit_target_pct:
            reason = "profit target"
        
        # Stop loss breach with streak
        if current_price < state.stop_loss:
            state.breach_count += 1
            # Scaled required streak: base + scale * current_profit * 100 (e.g., more profit, more confirmation needed)
            required_streak = self.breach_base_streak + int(self.breach_scale_factor * max(0, current_profit * 100))
            if state.breach_count >= required_streak:
                reason = "breach streak"
        else:
            state.breach_count = 0  # Reset if above SL
        
        # Trailing stop immediate if breached (but since streak, perhaps combined)
        if reason == "breach streak" and state.trailing_active:
            reason = "trailing stop"
        
        if reason:
            self.events.publish('sell_signal', {
                'symbol': symbol,
                'price': current_price,
                'quantity': self.quantity
            })
            self.logger.info(f"StoplossModule triggered SELL for {symbol} at {current_price} (reason: {reason})")
            # Reset state after sell
            state.entry_price = None
            state.stop_loss = None
            state.high_price = None
            state.breach_count = 0
            state.max_profit = 0.0
            state.trailing_active = False
            state.candle_history.clear()

    def on_connect(self, event):
        # Daily reset: reset breach counts or other daily vars; assuming no carry-over positions or adjust as needed
        for symbol in list(self.state.keys()):
            if self.state[symbol].entry_price:
                self.state[symbol].breach_count = 0  # Example reset
                # Could reset candle_history if daily, but probably not
            else:
                del self.state[symbol]  # Clean up unused

    def start(self):
        """Called when engine starts — subscribe to events, init state"""
        self.logger.info(f"Starting {self.__class__.__name__}")
        # Any additional startup logic if needed (e.g., load persisted state)

    def stop(self):
        """Called on engine stop — cleanup"""
        self.logger.info(f"Stopping {self.__class__.__name__}")
        # Any cleanup if needed (e.g., unsubscribe events, save state)

# Example config.yaml section for stoploss_params:
# stoploss_params:
#   initial_sl_pct: 0.02
#   breakeven_pct: 0.02
#   profit_lock_pct: 0.05
#   trail_start_pct: 0.08
#   atr_period: 14
#   atr_multiplier: 3.0
#   breach_base_streak: 3
#   breach_scale_factor: 0.5
#   profit_target_pct: 0.10
#   quantity: 900