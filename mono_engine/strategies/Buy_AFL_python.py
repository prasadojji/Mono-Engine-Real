from typing import Dict, Tuple
import pandas as pd
import numpy as np
import talib
from datetime import datetime
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from mono_engine.strategies.base_strategy import BaseStrategy

pd.options.mode.copy_on_write = True
from mono_engine.strategies.base_strategy import BaseStrategy


class Buy_AFL_python(BaseStrategy):
    """
    Converted AFL strategy focusing on buy signals only.
    Processes OHLCV data, resamples to base timeframe, computes indicators and conditions,
    and detects new buy signals based on MA1 transitions.
    """
    def __init__(self, params: Dict = None):
        super().__init__(params)
        # Default parameters from AFL
        default_params = {
            'base_timeframe': '5min',
            'fastLength': 12,
            'slowLength': 26,
            'signalSmoothing': 9,
            'RSI_Period': 14,
            'ADX_Period': 14,
            'KPeriod': 14,
            'DPeriod': 3,
            'BB_Period': 20,
            'BB_Width': 2,
            'lookbackPeriod': 20,
            'PeriodVol': 14,
            'StrengthThreshold': 65,
            'ATRPeriod_Trail': 14,
            'ATRMult_Trail': 2,
            'ATRPeriod_Scale': 14,
            'ATR_MA_Period': 20,
            'ATRMult_Scale': 1.5,
            'Base_Streak': 3,
            'Streak_Floor': 3,
            'Streak_Cap': 7,
            'RSI_Threshold': 35,
            'adxPeriod': 14,
            'maPeriod': 50,
            'slopeLookback': 5,
            'adxThreshold': 25,
            'slopeThreshold': 0.2,
            'donchianPeriod': 20,
            'Len': 10
        }
        if params:
            default_params.update(params)
        self.params = default_params
        self.debug = False  # Toggle for detailed logs
        self.base_df = pd.DataFrame()  # Accumulated 1-min data
        self.resampled_df = pd.DataFrame()  # Resampled to base_timeframe

    def on_data_update(self, data: Dict[str, pd.DataFrame]):
        if '1min' not in data or data['1min'].empty:
            return

        new_bars = data['1min']
        if self.base_df.empty:
            self.base_df = new_bars.copy()
        else:
            self.base_df = pd.concat([self.base_df, new_bars]).drop_duplicates(keep='last')

        # Resample to base timeframe
        agg_dict = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }
        self.resampled_df = self.base_df.resample(self.params['base_timeframe']).agg(agg_dict).dropna()

        if len(self.resampled_df) < 2:  # Need at least 2 bars for shifts
            return

        # Compute indicators and conditions
        self._compute_indicators()
        self._compute_conditions()

    def _compute_indicators(self):
        df = self.resampled_df

        # MACD
        df['MACDLine'], df['SignalLine'], df['MACDHist'] = talib.MACD(
            df['Close'], fastperiod=self.params['fastLength'], slowperiod=self.params['slowLength'],
            signalperiod=self.params['signalSmoothing']
        )

        # RSI
        df['RSIValue'] = talib.RSI(df['Close'], timeperiod=self.params['RSI_Period'])

        # ADX
        df['adxValue'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=self.params['ADX_Period'])

        # Parabolic SAR
        df['SAR1'] = talib.SAR(df['High'], df['Low'], acceleration=0.02, maximum=0.2)

        # Stochastic
        df['SlowK'], df['SlowD'] = talib.STOCH(
            df['High'], df['Low'], df['Close'],
            fastk_period=self.params['KPeriod'], slowk_period=self.params['DPeriod'], slowk_matype=0,
            slowd_period=self.params['DPeriod'], slowd_matype=0
        )

        # Bollinger Bands
        df['MiddleBand'] = talib.MA(df['Close'], timeperiod=self.params['BB_Period'])
        df['StdDev'] = talib.STDDEV(df['Close'], timeperiod=self.params['BB_Period'])
        df['UpperBand'] = df['MiddleBand'] + self.params['BB_Width'] * df['StdDev']
        df['LowerBand'] = df['MiddleBand'] - self.params['BB_Width'] * df['StdDev']

        # Candle Body to Wick ratio
        df['BodySize'] = np.abs(df['Close'] - df['Open'])
        df['CandleRange'] = df['High'] - df['Low']
        df['StrengthPct'] = (df['BodySize'] / (df['CandleRange'] + 1e-9)) * 100

        # Relative Strength Using Volume
        df['CandleStrength'] = (df['Close'] - df['Open']) * df['Volume']

        # Wick Analysis
        df['UpperWick'] = df['High'] - np.maximum(df['Open'], df['Close'])
        df['LowerWick'] = np.minimum(df['Open'], df['Close']) - df['Low']

        # Strength (Breakout vs Normal Move)
        df['ATR_14'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['ATR_Strength'] = (df['CandleRange'] / df['ATR_14']) * 100
        df['ATR_3'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=3)
        df['ATR3_Strength'] = (df['CandleRange'] / df['ATR_3']) * 100

        # Short term trend EMA(9) and EMA(21)
        df['ShortEMA'] = talib.EMA(df['Close'], timeperiod=9)
        df['LongEMA'] = talib.EMA(df['Close'], timeperiod=21)
        df['StrongTrend'] = df['adxValue'] > 25
        df['UpTrend'] = df['StrongTrend'] & (df['ShortEMA'] > df['LongEMA'])
        df['DownTrend'] = df['StrongTrend'] & (df['ShortEMA'] < df['LongEMA'])

        # VWAP Trend Confirmation (fixed calculation)
        df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['TPV'] = df['TP'] * df['Volume']
        df['CumulativeTPV'] = df.groupby(df.index.date)['TPV'].cumsum()
        df['CumulativeVolume'] = df.groupby(df.index.date)['Volume'].cumsum()
        df['VWAP'] = df['CumulativeTPV'] / df['CumulativeVolume']
        df['BullishTrend'] = df['Close'] > df['VWAP']
        df['BearishTrend'] = df['Close'] < df['VWAP']

        # Highest/Lowest Vol in lookback (fixed with loop for accuracy)
        lookback = self.params['lookbackPeriod']
        df['highestVol'] = np.nan
        df['highestVolPrice'] = np.nan
        df['lowestVol'] = np.nan
        df['lowestVolPrice'] = np.nan
        for i in range(lookback - 1, len(df)):
            window_vol = df['Volume'].iloc[i - lookback + 1:i + 1]
            window_close = df['Close'].iloc[i - lookback + 1:i + 1]
            max_idx = window_vol.idxmax()
            min_idx = window_vol.idxmin()
            df['highestVol'].iloc[i] = window_vol[max_idx]
            df['highestVolPrice'].iloc[i] = window_close[max_idx]
            df['lowestVol'].iloc[i] = window_vol[min_idx]
            df['lowestVolPrice'].iloc[i] = window_close[min_idx]

        # Volume MA and Spikes
        df['VolumeMA'] = talib.MA(df['Volume'], timeperiod=self.params['PeriodVol'])
        df['VolumeSpike'] = df['Volume'] > 1.3 * df['VolumeMA']
        df['VolumeSpike1'] = df['Volume'] > 1.2 * df['VolumeMA']

        # Enhanced VWAP
        df['EMA_Short'] = df['ShortEMA']
        df['EMA_Long'] = df['LongEMA']
        df['Momentum'] = talib.ROC(df['Close'], timeperiod=5)
        df['VolumeMA10'] = talib.MA(df['Volume'], timeperiod=10)
        df['BullishTrendVol'] = (df['Close'] > df['VWAP']) & (df['EMA_Short'] > df['EMA_Long']) & (df['Momentum'] > 0) & (df['Volume'] > df['VolumeMA10'])
        df['BearishTrendVol'] = (df['Close'] < df['VWAP']) & (df['EMA_Short'] < df['EMA_Long']) & (df['Momentum'] < 0) & (df['Volume'] > df['VolumeMA10'])

        # Momentum (RSI Divergence)
        price_high = df['High'].shift(1)
        rsi_high = df['RSIValue'].shift(1)
        price_high1 = price_high.shift(1)
        price_high2 = price_high.shift(2)
        rsi_high1 = rsi_high.shift(1)
        rsi_high2 = rsi_high.shift(2)
        df['BearishDivergence'] = (price_high > price_high1) & (price_high1 > price_high2) & (rsi_high < rsi_high1) & (rsi_high1 < rsi_high2)
        df['BullishDivergence'] = (price_high < price_high1) & (price_high1 < price_high2) & (rsi_high > rsi_high1) & (rsi_high1 > rsi_high2)
        df['ConfirmedBuy'] = df['BullishDivergence'].shift(1)
        df['ConfirmedSell'] = df['BearishDivergence'].shift(1)

        # MA Slope & ADX for sideways
        df['ma1'] = talib.MA(df['Close'], timeperiod=self.params['maPeriod'])
        df['maSlope'] = talib.ROC(df['ma1'], timeperiod=self.params['slopeLookback'])
        df['prevSlope'] = df['maSlope'].shift(1)
        df['prevADX'] = df['adxValue'].shift(1)
        df['TrendFilter'] = (df['prevADX'] > self.params['adxThreshold']) & (np.abs(df['prevSlope']) > self.params['slopeThreshold'])

        # Donchian Channel
        df['donchianHigh'] = df['High'].rolling(self.params['donchianPeriod']).max()
        df['donchianLow'] = df['Low'].rolling(self.params['donchianPeriod']).min()
        df['donchianRange'] = df['donchianHigh'] - df['donchianLow']
        df['donchianThreshold'] = df['donchianRange'].rolling(20).mean() * 0.5
        df['DonTrendFilter'] = df['donchianRange'] > df['donchianThreshold']

        # TSI
        atr10 = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=10)
        ratio = np.abs(df['Close'] - df['Close'].shift(10)) / atr10
        df['TSI'] = talib.MA(talib.MA(ratio, timeperiod=10), timeperiod=100)

        # ATR3P
        df['ATR3P'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=3)

        # Linear Regression Angle
        df['Slope'] = talib.LINEARREG_SLOPE(df['Close'], timeperiod=self.params['Len'])
        df['Angle'] = np.arctan(df['Slope']) * 180 / np.pi

        # CSS Composite Score
        df['CSI'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 0.001)
        green_vol = np.where(df['Close'] > df['Open'], df['Volume'].astype(float), 0.0)
        red_vol = np.where(df['Close'] < df['Open'], df['Volume'].astype(float), 0.0)
        df['VolImbalance'] = talib.EMA(green_vol - red_vol, timeperiod=5) / talib.EMA(df['Volume'].astype(float), timeperiod=5)
        body = np.abs(df['Close'] - df['Open'])
        upper_wick = df['High'] - np.maximum(df['Close'], df['Open'])
        lower_wick = np.minimum(df['Close'], df['Open']) - df['Low']
        df['BWR'] = body / (upper_wick + lower_wick + 0.001)
        thrust = df['Close'] - df['Close'].shift(1)
        atr_val = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['MomentumThrust'] = thrust / atr_val
        df['CSS'] = (40 * df['CSI'] + 20 * df['VolImbalance'] + 15 * df['BWR'] +
                     15 * df['MomentumThrust'] + 10 * (df['Angle'] / 45))

    def _compute_conditions(self):
        df = self.resampled_df

        # Collect all condition columns in a dict to add at once (avoids performance warnings)
        conditions_dict = {}

        # Basic conditions (using shifts for Ref(-1))
        conditions_dict['STD'] = (df['VWAP'] > df['VWAP'].shift(1)) & df['VolumeSpike']
        conditions_dict['GC'] = df['Open'].shift(1) < df['Close'].shift(1)
        conditions_dict['RC'] = df['Open'].shift(1) > df['Close'].shift(1)
        conditions_dict['B0'] = df['High'] > df['High'].shift(1)
        conditions_dict['B1'] = (df['StrengthPct'].shift(1) > 65) & conditions_dict['GC']
        conditions_dict['B101'] = (df['StrengthPct'].shift(1) < 10) & (conditions_dict['RC'] | conditions_dict['GC'])
        conditions_dict['B2'] = df['UpperWick'].shift(1) > df['LowerWick'].shift(1)
        conditions_dict['B21'] = df['UpperWick'].shift(1) < df['LowerWick'].shift(1)
        conditions_dict['B3'] = df['CandleStrength'].shift(1) > 0
        conditions_dict['B31'] = df['CandleStrength'].shift(1) > 120000
        conditions_dict['B32'] = df['CandleStrength'].shift(1) > 500000
        conditions_dict['B4'] = df['ATR_Strength'].shift(1) > 100
        conditions_dict['B41'] = df['ATR_Strength'].shift(1) > 80
        conditions_dict['B5'] = df['RSIValue'].shift(1) > 39
        conditions_dict['B6'] = df['UpTrend'].shift(1)
        conditions_dict['B7'] = df['BullishTrend'].shift(1)
        conditions_dict['B8'] = df['BullishTrendVol'].shift(1)
        conditions_dict['B9'] = df['ConfirmedBuy']
        conditions_dict['B10'] = df['DonTrendFilter'].shift(1)
        conditions_dict['B11'] = conditions_dict['B101'] & conditions_dict['B21']
        conditions_dict['B12'] = df['ATR3P'].shift(1) > 50

        # Combo formulas (buy-related)
        conditions_dict['CB1'] = conditions_dict['GC'] & (df['MACDLine'] > df['SignalLine']) & (df['RSIValue'] > 40) & (df['adxValue'] > 10) & (df['SlowK'] > df['SlowD']) & (df['High'] >= df['MiddleBand'])
        conditions_dict['CB2'] = conditions_dict['GC'] & (df['MACDLine'] > 5) & (df['RSIValue'] > 40) & (df['adxValue'] > 10) & (df['SlowK'] > df['SlowD']) & (df['High'] >= df['MiddleBand'])
        conditions_dict['CB3'] = conditions_dict['GC'] & (df['Open'] < df['LowerBand']) & (df['High'] >= df['MiddleBand'])
        conditions_dict['CB4'] = (df['RSIValue'] > 20) & (df['SlowK'] > df['SlowD']) & (df['adxValue'] > 40) & (df['High'] >= df['MiddleBand'])
        conditions_dict['CB5'] = conditions_dict['GC'] & (df['MACDLine'] > df['SignalLine']) & (df['RSIValue'] > 40) & (df['adxValue'] > 20) & (df['Open'] >= df['LowerBand'])
        conditions_dict['CB6'] = conditions_dict['GC'] & (df['RSIValue'] > 40) & (df['adxValue'] > 19) & (df['Open'] >= df['LowerBand']) & (df['SlowK'] > df['SlowD'])

        conditions_dict['CBR1'] = conditions_dict['RC'] & (df['MACDLine'] > df['SignalLine']) & (df['RSIValue'] > 40) & (df['adxValue'] > 10) & (df['SlowK'] > df['SlowD']) & (df['High'] >= df['MiddleBand']) & (df['Open'] < df['UpperBand']) & ((df['SlowK'] - df['SlowD']) < 1.6)
        conditions_dict['CBR2'] = conditions_dict['RC'] & (df['MACDLine'] > 5) & (df['RSIValue'] > 40) & (df['adxValue'] > 10) & (df['Open'] < df['UpperBand']) & ((df['SlowK'] - df['SlowD']) < 1.6) & (df['High'] >= df['MiddleBand'])
        conditions_dict['CBR3'] = conditions_dict['RC'] & (df['Open'] < df['LowerBand'].shift(1)) & (df['Open'] > df['UpperBand']) & ((df['SlowK'] - df['SlowD']) < 1.6) & (df['High'] >= df['MiddleBand'])
        conditions_dict['CBR4'] = conditions_dict['RC'] & (df['MACDLine'] > df['SignalLine']) & (df['RSIValue'] > 40) & (df['adxValue'] > 20) & (df['Open'] >= df['LowerBand'])

        conditions_dict['BR1'] = conditions_dict['STD'] & conditions_dict['RC'] & (df['MACDLine'] > df['SignalLine']) & (df['RSIValue'] > 40) & (df['adxValue'] > 25) & (df['SlowK'] > df['SlowD']) & (df['Open'] < df['UpperBand']) & (df['High'] >= df['MiddleBand']) & ((df['SlowK'] - df['SlowD']) > 1.6)
        conditions_dict['BR2'] = conditions_dict['STD'] & conditions_dict['RC'] & (df['MACDLine'] > 5) & (df['RSIValue'] > 40) & (df['adxValue'] > 25) & (df['Open'] < df['UpperBand']) & ((df['SlowK'] - df['SlowD']) > 1.6) & (df['High'] >= df['MiddleBand'])
        conditions_dict['BR3'] = conditions_dict['STD'] & conditions_dict['RC'] & (df['Open'] < df['LowerBand']) & (df['Open'] < df['UpperBand']) & ((df['SlowK'] - df['SlowD']) > 1.6) & (df['High'] >= df['MiddleBand'])
        conditions_dict['BR4'] = conditions_dict['STD'] & conditions_dict['RC'] & (df['MACDLine'] > df['SignalLine']) & (df['RSIValue'] > 40) & (df['adxValue'] > 20) & (df['Open'] >= df['LowerBand']) & (df['High'] >= df['MiddleBand'])
        conditions_dict['BR5'] = conditions_dict['STD'] & conditions_dict['RC'] & (df['Low'] < df['LowerBand']) & (df['High'] > df['High'].shift(1))
        conditions_dict['BR6'] = (df['Low'].shift(1) < df['LowerBand'].shift(1)) & (df['Close'].shift(1) > df['LowerBand'].shift(1))

        conditions_dict['NRC1'] = (df['High'] > df['High'].shift(1) + 3) & (df['High'] > df['High'].shift(2))
        conditions_dict['NRC2'] = (df['High'].shift(1) > df['High'].shift(2)) & (df['Low'].shift(1) > df['Low'].shift(2)) & (df['Open'] > df['Close'].shift(1)) & (df['Close'].shift(2) != df['High'].shift(2)) & (df['High'] > (df['Open'].shift(1) + df['Close'].shift(1)) / 2)
        conditions_dict['NRC3'] = (df['High'].shift(1) - df['Open'].shift(1) < df['Close'].shift(1) - df['Low'].shift(1)) & ((df['Open'].shift(1) - df['Close'].shift(1)) <= 2) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['NRC4'] = (df['Open'] > df['Close'].shift(1)) & (df['High'] > df['Open'].shift(1)) & (df['Open'].shift(2) > df['Close'].shift(2)) & (df['High'] > df['Open'].shift(2)) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['NRC5'] = (df['High'].shift(1) == df['Open'].shift(1)) & (df['Open'] > df['Close'].shift(1))

        conditions_dict['NRCB'] = (conditions_dict['BR1'] | conditions_dict['BR2'] | conditions_dict['BR3'] | conditions_dict['BR4'] | conditions_dict['BR5'] | conditions_dict['BR6']) & (conditions_dict['NRC1'] | conditions_dict['NRC2'] | conditions_dict['NRC3'] | conditions_dict['NRC4'] | conditions_dict['NRC5'])

        conditions_dict['BB1'] = conditions_dict['B1'] & conditions_dict['B2'] & conditions_dict['B3'] & conditions_dict['B5']
        conditions_dict['BB2'] = (conditions_dict['B2'] & conditions_dict['B3'] & conditions_dict['B4'] & conditions_dict['B5'] & conditions_dict['B6']) | (conditions_dict['B2'] & conditions_dict['B3'] & conditions_dict['B4'])
        conditions_dict['BB3'] = conditions_dict['B3'] & conditions_dict['B4'] & conditions_dict['B1'] & conditions_dict['B2'] & conditions_dict['B5'] & conditions_dict['B6']
        conditions_dict['BB4'] = conditions_dict['B4'] & conditions_dict['B1'] & conditions_dict['B2'] & conditions_dict['B5'] & conditions_dict['B6']
        conditions_dict['BB5'] = conditions_dict['B1'] & conditions_dict['B3'] & conditions_dict['B4'] & conditions_dict['B5']
        conditions_dict['BB6'] = conditions_dict['B3'] & conditions_dict['B4'] & conditions_dict['B5'] & conditions_dict['B6']
        conditions_dict['BB7'] = conditions_dict['B2'] & conditions_dict['B4'] & conditions_dict['B5'] & conditions_dict['B6'] & ~conditions_dict['RC']
        conditions_dict['BB8'] = conditions_dict['B8']
        conditions_dict['BB9'] = conditions_dict['B2'] & conditions_dict['B3'] & conditions_dict['B5'] & conditions_dict['B6']
        conditions_dict['BB10'] = (conditions_dict['B2'] & conditions_dict['B31'] & conditions_dict['B41']) | (conditions_dict['B3'] & conditions_dict['B31'] & conditions_dict['B32'] & conditions_dict['B41'] & conditions_dict['B12'])
        conditions_dict['BB11'] = (conditions_dict['B32'] & conditions_dict['B5']) | (conditions_dict['B3'] & conditions_dict['B31'] & conditions_dict['B4'] & conditions_dict['B12'])
        conditions_dict['BB12'] = (df['SlowK'] > df['SlowD']) & ((df['SlowK'] - df['SlowD']) > 3)
        conditions_dict['BB13'] = conditions_dict['B11'] & (df['High'] > df['High'].shift(1))
        conditions_dict['BB14'] = conditions_dict['B1'] & conditions_dict['B2'] & conditions_dict['B32'] & conditions_dict['B0'] & conditions_dict['B12']
        conditions_dict['BB15'] = conditions_dict['B2'] & conditions_dict['B3'] & conditions_dict['B12'] & conditions_dict['GC'] & (df['High'] > df['High'].shift(1))
        conditions_dict['BB16'] = conditions_dict['B21'] & conditions_dict['B41'] & conditions_dict['B12'] & conditions_dict['RC'] & (df['High'] > df['High'].shift(1))
        conditions_dict['BB17'] = conditions_dict['GC'] & (df['High'] > df['High'].shift(1)) & ((df['Open'].shift(1) - df['Low'].shift(1)) < 1) & (df['CSS'] > 70)

        conditions_dict['CBB0'] = conditions_dict['CB1'] | conditions_dict['CB2'] | conditions_dict['CB3'] | conditions_dict['CB4'] | conditions_dict['CB5'] | conditions_dict['CB6']
        conditions_dict['CBB1'] = conditions_dict['CBB0'] & (df['High'] > df['High'].shift(1) + 3) & (df['Open'] > df['Open'].shift(1)) & (df['High'].shift(1) > df['High'].shift(2)) & (df['Low'].shift(1) > df['Low'].shift(2))
        conditions_dict['CBB2'] = conditions_dict['CBB0'] & (df['Open'] < df['Close'].shift(1)) & (df['Low'].shift(1) > df['Low'].shift(2)) & (df['High'] > df['High'].shift(1) + 3) & (df['High'] > df['High'].shift(2))
        conditions_dict['CBB3'] = conditions_dict['CBB0'] & (df['Open'] > df['Close'].shift(1)) & (df['High'] > df['High'].shift(1) + 3) & (df['Open'].shift(1) > df['Close'].shift(2))
        conditions_dict['CBB4'] = conditions_dict['CBB0'] & (df['Open'] > df['Close'].shift(1)) & (df['High'] > df['High'].shift(1) + 3) & ((df['Open'].shift(1) - df['Close'].shift(2)) < 1)
        conditions_dict['CBB5'] = conditions_dict['CBB0'] & (df['Open'] < df['Close'].shift(1)) & (df['Close'].shift(1) == df['High'].shift(1)) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['CBB6'] = conditions_dict['CBB0'] & (df['Open'] < df['Close'].shift(1)) & (df['Open'] - df['Low'] <= (df['Open'] * 0.0100)) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['CBB7'] = (conditions_dict['CBB0'] & (df['Open'].shift(1) == df['Low'].shift(1)) & (df['Open'] < df['Close'].shift(1)) & (df['High'] > df['High'].shift(1) + 3)) | (conditions_dict['CBB0'] & (df['High'].shift(1) > df['High'].shift(2)) & (df['Open'] < df['Close'].shift(1)) & (df['High'] > df['High'].shift(1) + 3))
        conditions_dict['CBB8'] = conditions_dict['CBB0'] & ((df['Close'].shift(1) - df['Open'].shift(1)) > 9) & ((df['Close'].shift(1) - df['Open'].shift(1)) < 13)

        conditions_dict['CBR'] = conditions_dict['CBR1'] | conditions_dict['CBR2'] | conditions_dict['CBR3'] | conditions_dict['CBR4']

        conditions_dict['CBBR1'] = conditions_dict['CBR'] & (df['Open'] > df['High'].shift(1))
        conditions_dict['CBBR2'] = conditions_dict['CBR'] & ((df['High'].shift(1) - df['Open'].shift(1)) < 0.5)
        conditions_dict['CBBR3'] = conditions_dict['CBR'] & (df['High'] > df['High'].shift(1) + 3) & (df['High'] > df['High'].shift(2)) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['CBBR4'] = conditions_dict['CBR'] & (df['High'].shift(1) > df['High'].shift(2)) & (df['Low'].shift(1) > df['Low'].shift(2)) & (df['Open'] > df['Close'].shift(1)) & (df['Close'].shift(2) != df['High'].shift(2)) & (df['High'] > (df['Open'].shift(1) + df['Close'].shift(1)) / 2) & (df['High'] > df['High'].shift(1))
        conditions_dict['CBBR5'] = conditions_dict['CBR'] & ((df['High'].shift(1) - df['Open'].shift(1)) < (df['Close'].shift(1) - df['Low'].shift(1))) & ((df['Open'].shift(1) - df['Close'].shift(1)) <= 2) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['CBBR6'] = conditions_dict['CBR'] & (df['Open'] > df['Close'].shift(1)) & (df['High'] > df['Open'].shift(1)) & (df['Open'].shift(2) > df['Close'].shift(2)) & (df['High'] > df['Open'].shift(2)) & (df['High'] > df['High'].shift(1) + 3)
        conditions_dict['CBBR7'] = conditions_dict['CBR'] & (df['High'].shift(1) == df['Open'].shift(1)) & (df['Open'] > df['Close'].shift(1))

        # Green (buy signal combos)
        conditions_dict['Green'] = (((conditions_dict['BB1'] | conditions_dict['BB2'] | conditions_dict['BB3'] | conditions_dict['BB4'] | conditions_dict['BB5'] | conditions_dict['BB6'] | conditions_dict['BB7'] | conditions_dict['BB8'] | conditions_dict['BB9'] | conditions_dict['BB10'] | conditions_dict['BB11']) & conditions_dict['BB12'].shift(1) & conditions_dict['B0']) | conditions_dict['BB13'] | conditions_dict['BB14'] | conditions_dict['BB15'] | conditions_dict['BB16'] | conditions_dict['BB17']) & conditions_dict['B0']

        # Red
        conditions_dict['Red'] = conditions_dict['CBB1'] | conditions_dict['CBB2'] | conditions_dict['CBB3'] | conditions_dict['CBB4'] | conditions_dict['CBB5'] | conditions_dict['CBB6'] | conditions_dict['CBB7'] | conditions_dict['CBB8'] | conditions_dict['CBBR1'] | conditions_dict['CBBR2'] | conditions_dict['CBBR3'] | conditions_dict['CBBR4'] | conditions_dict['CBBR5'] | conditions_dict['CBBR6'] | conditions_dict['CBBR7'] | conditions_dict['NRCB']

        # MA1
        conditions_dict['MA1'] = conditions_dict['Green'] | conditions_dict['Red']

        # Add all conditions at once to avoid warnings
        conditions_df = pd.DataFrame(conditions_dict, index=df.index)
        df = pd.concat([df, conditions_df], axis=1)

        self.resampled_df = df  # Update back

        # Optional debug: Print reasons if signal
        if self.debug and len(df) > 1 and df['MA1'].iloc[-1] and not df['MA1'].iloc[-2]:
            reasons = []
            bb_cols = [col for col in df.columns if col.startswith('BB')]
            cbb_cols = [col for col in df.columns if col.startswith('CBB')]
            cbbr_cols = [col for col in df.columns if col.startswith('CBBR')]
            for col in bb_cols + cbb_cols + cbbr_cols:
                if df[col].iloc[-1]:
                    reasons.append(col)
            print(f"Buy signal triggered by: {', '.join(reasons)}")

    def should_enter(self) -> Tuple[bool, float | None, str]:
        """Return (enter_signal, price, buy_reason) for PnL tracking"""
        if len(self.resampled_df) < 2:
            return False, None, 'unknown'

        current_ma1 = self.resampled_df['MA1'].iloc[-1]
        prev_ma1   = self.resampled_df['MA1'].iloc[-2]

        if current_ma1 and not prev_ma1:
            reason = self._get_buy_reason()
            price  = self.resampled_df['High'].iloc[-1]
            return True, price, reason

        return False, None, 'unknown'


    def _get_buy_reason(self) -> str:
        """Returns exact trigger name(s) — used by PnL for per-reason win-rate"""
        df = self.resampled_df
        reasons = []
        trigger_cols = [col for col in df.columns 
                        if col.startswith(('BB', 'CBB', 'CBBR', 'NRCB', 'Green'))]

        for col in trigger_cols:
            if df[col].iloc[-1]:          # signal is True on latest bar
                reasons.append(col)

        return ', '.join(reasons) if reasons else 'MA1'


    def should_exit(self) -> Tuple[bool, float | None]:
        return False, None


    def reset_day(self):
        self.base_df = pd.DataFrame()
        self.resampled_df = pd.DataFrame()


# =============================================================================
# Standalone test (UPDATED to use new should_enter signature)
# =============================================================================
if __name__ == "__main__":
    import sqlite3
    import json
    from tabulate import tabulate
    import os

    # Load watchlist
    watchlist_path = 'watchlist.json'
    if not os.path.exists(watchlist_path):
        print(f"watchlist.json not found at {watchlist_path} — skipping.")
    else:
        with open(watchlist_path, 'r') as f:
            watchlist = json.load(f)

        signals = []
        db_path = 'mono_engine_data.db'
        conn = sqlite3.connect(db_path)

        for item in watchlist:
            symbol = item.get('id', item.get('symbol'))
            if not symbol:
                continue

            df = pd.read_sql(f"""
                SELECT timestamp as ts, open as Open, high as High, low as Low, 
                       close as Close, volume as Volume 
                FROM historical_1min 
                WHERE symbol = '{symbol}'
                ORDER BY timestamp
            """, conn, parse_dates=['ts'], index_col='ts')

            if df.empty:
                continue

            strategy = Buy_AFL_python()
            strategy.debug = False

            batch_size = 20
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                strategy.on_data_update({'1min': batch})

                # === UPDATED CALL (now returns 3 values) ===
                enter, price, reason = strategy.should_enter()

                if enter:
                    signals.append({
                        'Time': batch.index[-1],
                        'Symbol': symbol,
                        'Buy Trigger Price': round(price, 2),
                        'Buy Reason': reason
                    })

        conn.close()

        # Final summary table
        if signals:
            signals_df = pd.DataFrame(signals)
            signals_df = signals_df.sort_values('Time', ascending=False).reset_index(drop=True)
            signals_df.insert(0, 'SNo', range(1, len(signals_df) + 1))
            print("\n" + "="*100)
            print("HISTORICAL BUY SIGNALS WITH REASONS")
            print("="*100)
            print(tabulate(signals_df, headers='keys', tablefmt='grid', showindex=False))
        else:
            print("No buy signals detected in the historical data.")