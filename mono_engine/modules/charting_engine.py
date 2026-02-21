import logging
import threading
import time
import webbrowser
import pandas as pd
from typing import List

from pycharting import plot, stop_server  # Correct import — functional API

class ChartingEngine:
    def __init__(
        self,
        market_data,
        state_trade_object,
        timeframes: List[str] = None,
        visible_candles: int = 500,
        port: int = None  # Auto if None
    ):
        self.market_data = market_data
        self.state = state_trade_object
        self.timeframes = timeframes or ["1min", "5min"]
        self.visible_candles = visible_candles
        self.port = port

        # Symbols for charting (spot + top options)
        spot = f"{self.market_data.sensex_spot_token}_BSE" if self.market_data.sensex_spot_token else None
        options = [f"{item['token']}_BFO" for item in self.market_data.watchlist[:6]]  # Top 6 for good view
        self.symbols = [s for s in ([spot] if spot else []) + options if s]

        # Session IDs (one per symbol for separate tabs)
        self.session_ids = {sym: f"mono_{i}" for i, sym in enumerate(self.symbols)}

        # First plot (opens browser tabs)
        self._update_charts(open_browser=True)

        # Background live update
        threading.Thread(target=self._update_loop, daemon=True).start()

        logging.info("pycharting ChartingEngine started — live charts in browser tabs")

    def _get_series(self, symbol: str, tf: str = "1min"):
        df = self.market_data.get_candles(symbol, tf)
        if df.empty:
            return None, None, None, None, None
        df = df.tail(self.visible_candles).copy().sort_index()
        index = df.index.astype('int64') // 10**6  # ms timestamps for uPlot
        o = df['open'].tolist()
        h = df['high'].tolist()
        l = df['low'].tolist()
        c = df['close'].tolist()
        return index, o, h, l, c

    def _compute_ema(self, close_list, period=20):
        if len(close_list) < period:
            return [None] * len(close_list)
        df = pd.Series(close_list)
        return df.ewm(span=period, adjust=False).mean().tolist()

    def _update_charts(self, open_browser=False):
        try:
            for symbol in self.symbols:
                # Main 5min candles
                index, o, h, l, c = self._get_series(symbol, "5min")
                if index is None:
                    continue

                # EMA overlay
                ema20 = self._compute_ema(c, 20)
                overlays = {"EMA20": ema20} if len(ema20) == len(c) else {}

                # Volume subplot
                vol_df = self.market_data.get_candles(symbol, "1min")
                if not vol_df.empty:
                    vol = vol_df['volume'].tail(self.visible_candles).fillna(0).tolist()
                    subplots = {"Volume": vol}
                else:
                    subplots = {}

                plot(
                    index,
                    o,
                    h,
                    l,
                    c,
                    overlays=overlays,
                    subplots=subplots,
                    session_id=self.session_ids[symbol],
                    port=self.port,
                    open_browser=open_browser and symbol == self.symbols[0],
                    server_timeout=5.0
                )

            logging.debug("Charts updated for %s symbols", len(self.symbols))
        except Exception as e:
            logging.error(f"Chart update error: {e}")

    def _update_loop(self):
        while True:
            time.sleep(5)  # Live refresh every 5s
            self._update_charts(open_browser=False)

    def stop(self):
        stop_server()  # Clean shutdown
        logging.info("pycharting server stopped")