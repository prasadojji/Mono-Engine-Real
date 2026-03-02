# mono_engine/modules/strategy.py
import logging
import pandas as pd
from collections import defaultdict
from datetime import datetime
from typing import Dict
import time

from mono_engine.modules.base import BaseModule
from mono_engine.strategies.base_strategy import BaseStrategy
from mono_engine.strategies.Buy_AFL_python import Buy_AFL_python  # Updated import

class StrategyModule(BaseModule):
    """
    Strategy Module (Buy/Sell Logic Engine)
    - Aggregates raw ticks into 1-min candles per symbol
    - Feeds to per-symbol strategy instances (Buy_AFL_python)
    - Emits buy_signal / sell_signal events per symbol
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        
        # Use Buy_AFL_python
        self.strategy_class = Buy_AFL_python
        
        # Configurable base timeframe
        self.base_timeframe = self.engine.config.get('strategy_params', {}).get('base_timeframe', '5min')
        self.logger.info(f"Using base timeframe: {self.base_timeframe}")
        
        # Per-symbol strategy instances
        self.strategies = {}  # symbol -> BaseStrategy instance
        
        # Candle aggregation state per symbol (1min only for now)
        self.candle_data = defaultdict(lambda: {
            'open': None, 'high': None, 'low': None, 'close': None, 'volume': 0,
            'current_time': None
        })

    def start(self):
        self.events.subscribe('on_tick', self._on_tick)  # Use existing EVENT_TICK
        self.events.subscribe('on_connect', lambda _: self._reset_all_strategies())  # Daily reset
        self.logger.info("StrategyModule started — aggregating 1-min candles for all watchlist symbols")

    def stop(self):
        self.events.unsubscribe('on_tick', self._on_tick)
        self.logger.info("StrategyModule stopped")

    def _reset_all_strategies(self):
        for strategy in self.strategies.values():
            strategy.reset_day()
        self.logger.info("Reset all strategies for new day")

    def _get_or_create_strategy(self, symbol: str) -> BaseStrategy:
        if symbol not in self.strategies:
            params = self.engine.config.get('strategy_params', {})
            params['base_timeframe'] = self.base_timeframe  # Pass to strategy
            self.strategies[symbol] = self.strategy_class(params=params)
            self.strategies[symbol].debug = True  # Enable reasons logging
            self.logger.info(f"Created {self.strategy_class.__name__} instance for symbol: {symbol}")
        return self.strategies[symbol]

    def _on_tick(self, tick: Dict):
        symbol = tick.get('symbol')
        if not symbol:
            self.logger.debug("Tick missing symbol — skipped")
            return

        # Log every tick for troubleshooting
        ltp = tick.get('ltp')
        vol = tick.get('vol', 0)
        ts = datetime.fromtimestamp(tick.get('exchange_time', time.time()))
        self.logger.debug(f"Tick received: {symbol} LTP={ltp} Vol={vol} Time={ts}")

        # Only process symbols in watchlist
        watchlist_tokens = {f"{item['token']}_BFO" for item in self.engine.modules['market_data'].watchlist}
        if symbol not in watchlist_tokens and symbol != '-51_BSE':
            self.logger.debug(f"Tick for non-watchlist symbol {symbol} — skipped")
            return

        # Aggregate candle
        minute_ts = ts.replace(second=0, microsecond=0)
        data = self.candle_data[symbol]

        if data['current_time'] is None or minute_ts > data['current_time']:
            # New bar — push previous complete bar to strategy
            # New bar — push previous complete bar to strategy
            if data['current_time'] is not None:
                df_1min = pd.DataFrame([{
                    'Open': data['open'],
                    'High': data['high'],
                    'Low': data['low'],
                    'Close': data['close'],
                    'Volume': data['volume']
                }], index=[data['current_time']])
                
                strategy = self._get_or_create_strategy(symbol)
                strategy.on_data_update({'1min': df_1min})
                
                # === CRITICAL FIX: Publish 1min_bar_closed so StoplossModule runs ===
                bar_data = {
                    'symbol': symbol,
                    'bar': {
                        'ts': data['current_time'],
                        'open': float(data['open']),
                        'high': float(data['high']),
                        'low': float(data['low']),
                        'close': float(data['close']),
                        'volume': int(data['volume'])
                    }
                }
                self.events.publish('1min_bar_closed', bar_data)
                
                self._check_and_publish_signals(symbol)
                self.logger.debug(f"Fed 1min candle + published '1min_bar_closed' for {symbol} @ {data['current_time']}")

            # Start new bar
            data['open'] = data['high'] = data['low'] = data['close'] = ltp
            data['volume'] = vol
            data['current_time'] = minute_ts
        else:
            # Update current bar
            data['high'] = max(data['high'], ltp)
            data['low'] = min(data['low'], ltp)
            data['close'] = ltp
            data['volume'] += vol  # Cumulative

    def _check_and_publish_signals(self, symbol: str):
        strategy = self._get_or_create_strategy(symbol)
        
        # FIXED: Safe unpacking - now handles 2 or 3 return values from should_enter()
        result = strategy.should_enter()
        if isinstance(result, tuple):
            if len(result) == 3:
                enter, price, reason = result
            else:
                enter, price = result
                reason = 'unknown'
        else:
            enter = result
            price = None
            reason = 'unknown'

        if enter:
            subscribed_symbol = symbol  # already token_BFO
            self.events.publish('buy_signal', {
                'price': price or 0.0,
                'symbol': symbol,
                'subscribed_symbol': subscribed_symbol,
                'quantity': 900,
                'buy_reason': reason   # ← Added for PnLModule
            })
            self.logger.info(f"{strategy.__class__.__name__} BUY SIGNAL for {symbol} at {price} | Reason: {reason}")

        # should_exit remains unchanged (still returns 2 values)
        exit_, price = strategy.should_exit()
        if exit_:
            self.events.publish('sell_signal', {
                'price': price or 0.0,
                'symbol': symbol,
                'subscribed_symbol': symbol,
                'quantity': 900
            })
            self.logger.info(f"{strategy.__class__.__name__} SELL SIGNAL for {symbol} at {price}")