import pandas as pd
from datetime import datetime
from typing import List
import webbrowser
import os

from pyecharts import options as opts
from pyecharts.charts import Grid, Kline, Bar
from pyecharts.globals import ThemeType

class ChartingEngine:
    def __init__(
        self,
        market_data,
        state_trade_object,  # Pass state_module.state (TradeState instance)
        timeframes: List[str] = None,
        visible_candles: int = 250,
        html_file: str = "live_chart.html"
    ):
        self.market_data = market_data
        self.state = state_trade_object  # Direct access to TradeState
        self.timeframes = timeframes or ["1min", "5min"]
        self.visible_candles = visible_candles
        self.html_file = html_file
        self.first_render = True
        # Open browser immediately on init (blank chart ready for data)
        abs_path = os.path.abspath(self.html_file)
        webbrowser.open(f"file://{abs_path}")

        # Open blank chart immediately
        grid = Grid(init_opts=opts.InitOpts(width="1800px", height=f"{500 * len(self.timeframes)}px", theme=ThemeType.DARK))
        grid.render(self.html_file)  # Render empty
        abs_path = os.path.abspath(self.html_file)
        webbrowser.open(f"file://{abs_path}")

    def _prepare_data(self, df: pd.DataFrame):
        if df.empty:
            return [], [], [], [], pd.DataFrame()
        df = df.tail(self.visible_candles).copy()
        df = df.sort_index()
        df["date_str"] = df.index.strftime("%m-%d %H:%M")

        kline_data = df[["open", "close", "low", "high"]].values.tolist()
        xaxis_data = df["date_str"].tolist()

        df["vol_up"] = df["volume"].where(df["close"] >= df["open"], 0)
        df["vol_down"] = df["volume"].where(df["close"] < df["open"], 0)
        vol_up = df["vol_up"].tolist()
        vol_down = df["vol_down"].tolist()

        return kline_data, xaxis_data, vol_up, vol_down, df

    def _add_trade_markers(self, chart: Kline, df: pd.DataFrame, xaxis_data: List[str]):
        buy_points = []
        sell_points = []

        def find_closest_idx(t: datetime):
            if t is None or df.empty:
                return None
            diffs = (df.index - t).abs()
            return diffs.idxmin()

        # Historical completed trades
        for trade in self.state.trade_history:
            entry_idx = find_closest_idx(trade.get("entry_time"))
            exit_idx = find_closest_idx(trade.get("exit_time"))

            if entry_idx is not None:
                row = df.loc[entry_idx]
                idx = df.index.get_loc(entry_idx)
                buy_points.append(opts.MarkPointItem(
                    coord=[xaxis_data[idx], row["low"] * 0.995],
                    itemstyle_opts=opts.ItemStyleOpts(color="lime")
                ))
            if exit_idx is not None:
                row = df.loc[exit_idx]
                idx = df.index.get_loc(exit_idx)
                sell_points.append(opts.MarkPointItem(
                    coord=[xaxis_data[idx], row["high"] * 1.005],
                    itemstyle_opts=opts.ItemStyleOpts(color="red")
                ))

        # Current open position
        if self.state.in_trade and self.state.entry_details:
            entry_idx = find_closest_idx(self.state.entry_details.time)
            if entry_idx is not None:
                row = df.loc[entry_idx]
                idx = df.index.get_loc(entry_idx)
                buy_points.append(opts.MarkPointItem(
                    coord=[xaxis_data[idx], row["low"] * 0.995],
                    itemstyle_opts=opts.ItemStyleOpts(color="lime")
                ))

        chart.set_series_opts(
            markpoint_opts=opts.MarkPointOpts(
                data=buy_points + sell_points,
                symbol="triangle",
                symbol_size=20
            )
        )

        # Current entry price horizontal line
        if self.state.in_trade and self.state.entry_details:
            chart.set_series_opts(
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(y=self.state.entry_details.price, name="Entry")],
                    linestyle_opts=opts.LineStyleOpts(color="lime", type_="dashed")
                )
            )

    def update(self):
        # Get SENSEX spot symbol (underlying for charting)
        spot_symbol = f"{self.market_data.sensex_spot_token}_BSE" if getattr(self.market_data, 'sensex_spot_token', None) else None
        if not spot_symbol:
            logging.warning("SENSEX spot token not available — skipping chart update")
            return

        grid = Grid(init_opts=opts.InitOpts(
            width="1800px",
            height=f"{500 * len(self.timeframes)}px",
            theme=ThemeType.DARK
        ))

        has_data = False
        for idx, tf in enumerate(self.timeframes):
            df = self.market_data.get_candles(spot_symbol, tf)
            kline_data, xaxis_data, vol_up, vol_down, df_prep = self._prepare_data(df)

            if not xaxis_data:
                continue

            has_data = True

            # Candlestick Kline
            kline = (
                Kline()  # Fixed typo: Klie() → Kline()
                .add_xaxis(xaxis_data)
                .add_yaxis(
                    series_name="Kline",
                    y_axis=kline_data,
                    itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c")
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=f"SENSEX {tf.upper()} - Mono Engine Live", pos_top=f"{idx * 5}%"),
                    xaxis_opts=opts.AxisOpts(is_show=(idx == len(self.timeframes) - 1)),
                    yaxis_opts=opts.AxisOpts(),
                    datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)],
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
                )
            )

            # Volume bars
            bar = (
                Bar()
                .add_xaxis(xaxis_data)
                .add_yaxis("Vol Up", vol_up, stack="volume", itemstyle_opts=opts.ItemStyleOpts(color="#00da3c"))
                .add_yaxis("Vol Down", vol_down, stack="volume", itemstyle_opts=opts.ItemStyleOpts(color="#ec0000"))
                .set_global_opts(yaxis_opts=opts.AxisOpts(is_show=False))
            )

            # Trade markers
            self._add_trade_markers(kline, df_prep, xaxis_data)

            # Overlap and add to grid
            overlap = kline.overlap(bar)
            top_percent = f"{idx * (100 / len(self.timeframes))}%"
            grid.add(overlap, grid_opts=opts.GridOpts(pos_top=top_percent, height=f"{90 // len(self.timeframes)}%"))

        # Render if data exists or first time (opens blank chart immediately)
        if has_data or self.first_render:
            grid.render(self.html_file)
            if self.first_render:
                abs_path = os.path.abspath(self.html_file)
                webbrowser.open(f"file://{abs_path}")
                self.first_render = False