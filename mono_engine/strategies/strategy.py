# mono_engine/modules/strategy.py
import logging
import pandas as pd
from collections import defaultdict
from datetime import datetime
from typing import Dict

from .base import BaseModule
from mono_engine.strategies.afl_strategy import AFLStrategy  # Import your pluggable strategy

class StrategyModule(BaseModule):
    """
    Strategy Module (Buy/Sell Logic Engine)
    - Aggregates raw ticks into 1-min candles
    - Feeds to AFLStrategy
    - Emits buy_signal / sell_signal events on rising edges
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        
        # Load your AFL strategy (params from config if needed)
        self.strategy = AFLStrategy(params=engine.config.get('strategy_params', {}))
        
        # Candle aggregation state (per symbol)
        self.candle_data = defaultdict(lambda: {
            'open': None, 'high': None, 'low': None, 'close': None, 'volume': 0,
            'current_time': None
        })
        
        # Assume single primary scrip for now (from watchlist or config)
        self.primary_symbol = engine.config.get('primary_symbol', None)  # Set in config.yaml, e.g., first watchlist token

    def start(self):
        self.events.subscribe('on_tick', self._on_tick)  # Use existing EVENT_TICK
        self.events.subscribe('on_connect', lambda _: self.strategy.reset_day())  # Daily reset
        self.logger.info("StrategyModule started — aggregating 1-min candles and running AFLStrategy")

    def stop(self):
        self.events.unsubscribe('on_tick', self._on_tick)
        self.logger.info("StrategyModule stopped")

    def _on_tick(self, tick: Dict):
        symbol = tick.get('symbol')
        if not symbol or symbol != self.primary_symbol:
            return  # Filter to primary (extend for multi later)

        ltp = tick.get('ltp')
        vol = tick.get('vol', 0)  # Or qty if incremental
        ts = datetime.fromtimestamp(tick.get('exchange_time', time.time()))  # Use exchange time

        # Truncate to minute
        minute_ts = ts.replace(second=0, microsecond=0)

        data = self.candle_data[symbol]
        if data['current_time'] is None or minute_ts > data['current_time']:
            # New bar — push previous complete bar
            if data['current_time'] is not None:
                df = pd.DataFrame([{
                    'Open': data['open'],
                    'High': data['high'],
                    'Low': data['low'],
                    'Close': data['close'],
                    'Volume': data['volume']
                }], index=[data['current_time']])
                self.strategy.on_data_update({'1min': df})
                self._check_and_publish_signals()

            # Start new bar
            data['open'] = data['high'] = data['low'] = data['close'] = ltp
            data['volume'] = vol
            data['current_time'] = minute_ts
        else:
            # Update current bar
            data['high'] = max(data['high'], ltp)
            data['low'] = min(data['low'], ltp)
            data['close'] = ltp
            data['volume'] += vol  # Cumulative if incremental

    def _check_and_publish_signals(self):
        enter, price = self.strategy.should_enter()
        if enter and not self.engine.modules['state'].is_in_trade():
            # Trade CE only for long
            ce_item = next((item for item in self.engine.modules['market_data'].watchlist if item['type'] == 'CE'), None)
            if ce_item:
                symbol = ce_item['symbol']
                token = f"{ce_item['token']}_BFO"
                self.events.publish('buy_signal', {'price': price or 0.0, 'symbol': symbol, 'token': token, 'quantity': 900})
                self.logger.info(f"BUY SIGNAL emitted for {symbol} at {price}")
            else:
                self.logger.warning("No CE in watchlist — no buy signal")

        exit_, price = self.strategy.should_exit()
        if exit_ and self.engine.modules['state'].is_in_trade():
            ce_item = next((item for item in self.engine.modules['market_data'].watchlist if item['type'] == 'CE'), None)
            if ce_item:
                symbol = ce_item['symbol']
                token = f"{ce_item['token']}_BFO"
                self.events.publish('sell_signal', {'price': price or 0.0, 'symbol': symbol, 'token': token, 'quantity': 900})
                self.logger.info(f"SELL SIGNAL emitted for {symbol} at {price}")