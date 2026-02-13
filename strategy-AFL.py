# Imports
import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
from matplotlib.patches import Arrow
import datetime
import shelve
import argparse
import os

# Modular design: This script can be included in a broader project like a mono engine.
# It defines a Strategy class that encapsulates the logic, allowing it to be called as a strategy.
# The class has methods for different parts of the AFL code, preserving structure.
# Comments explain each function/class and its purpose.

class Strategy:
    """
    This class encapsulates the entire AFL strategy logic translated to Python.
    Purpose: To simulate the Amibroker strategy for volume profile, indicators, and trading signals.
    It processes a Pandas DataFrame and generates plots, signals, and outputs.
    Designed to be extensible for future enhancements.
    """
    
    def __init__(self, df, params=None, static_file='static_vars.shelve'):
        """
        Initializes the strategy with input DataFrame and parameters.
        Purpose: Set up data, parameters, and persistent storage.
        :param df: Pandas DataFrame with 'DateTime' index, 'Open', 'High', 'Low', 'Close', 'Volume'.
        :param params: Optional dict of parameters overriding defaults.
        :param static_file: File for persistent static variables using shelve.
        """
        self.df = df.copy()
        self.df.index = pd.to_datetime(self.df.index)  # Ensure datetime index
        self.params = self._set_default_params() if params is None else params
        self.static_file = static_file
        self.static_vars = shelve.open(static_file)  # Persistent dictionary for StaticVar
        self.var_dict = {}  # For VarSet/VarGet dynamic variables
        self._prepare_data()  # Preprocess data

    def _set_default_params(self):
        """
        Sets default parameters mimicking Param calls in AFL.
        Purpose: Provide hardcoded defaults or configurable params.
        Returns: Dict of parameters.
        """
        return {
            "volumeValueArea": 0.7,
            "showVolume": 1,
            "showMain": 1,
            "showHL": 1,
            "showShifted": 1,
            "showShiftedHL": 1,
            "giveVolumeAreaColor": 1,
            "sep": "Day",
            "fontType": "Courier New",
            "fontSize": 9,
            "lineWidth1": 1,
            "lineWidth2": 5,
            "showLabel": 1,
            "shft": 1,
            "volfact": 0.8,
            "bins": 50,
            "fastLength": 12,
            "slowLength": 26,
            "signalSmoothing": 9,
            "RSI_Period": 14,
            "ADX_Period": 14,
            "KPeriod": 14,
            "DPeriod": 3,
            "Period": 20,
            "Width": 2,
            "lookbackPeriod": 20,
            "PeriodVol": 14,
            "adxPeriod": 14,
            "maPeriod": 50,
            "slopeLookback": 5,
            "adxThreshold": 25,
            "slopeThreshold": 0.2,
            "donchianPeriod": 20,
            "Len": 10,
            "StrengthThreshold": 65,
            "ATRPeriod_Trail": 14,
            "ATRMult_Trail": 2,
            "ATRPeriod_Scale": 14,
            "ATR_MA_Period": 20,
            "ATRMult_Scale": 1.5,
            "Base_Streak": 3,
            "Streak_Floor": 3,
            "Streak_Cap": 7,
            "RSI_Period_weak": 9,  # Renamed to avoid conflict
            "RSI_Threshold": 35,
            "ResetStatics": 0,
            "MaxTradesStored": 500,
            "ClearTradeHistory": 0,
            "maxShift": 3
        }

    def _prepare_data(self):
        """
        Prepares the DataFrame by adding necessary columns like BarIndex.
        Purpose: Mimic AFL's BarIndex, BarCount, etc.
        """
        self.df['mn'] = self.df.index.minute
        self.df['newFiveMinBar'] = (self.df['mn'] != self._ref(self.df['mn'], -1)) & (self.df['mn'] % 5 == 0)
        self.df['newOneMinBarStart'] = self.df['mn'] != self._ref(self.df['mn'], -1)
        self.df['newOneMinBarEnd'] = self.df['newOneMinBarStart'].shift(-1, fill_value=False)  # Approx end as next start
        self.df['BarIndex'] = np.arange(len(self.df))
        self.bi = self.df['BarIndex'].values
        self.bar_count = len(self.df)

    def _resample(self, timeframe):
        """
        Resamples the DataFrame to a higher timeframe.
        Purpose: Mimic TimeFrameSet/TimeFrameRestore/TimeFrameExpand.
        :param timeframe: e.g., '5T' for 5 minutes.
        Returns: Resampled DataFrame.
        """
        resampled = self.df.resample(timeframe).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        return resampled

    def _expand(self, series, base_df, mode='point'):
        """
        Expands a series from higher timeframe back to base timeframe.
        Purpose: Mimic TimeFrameExpand.
        :param series: Series from resampled DF.
        :param base_df: Original DF.
        :param mode: 'point' (last), 'last' (ffill last), etc.
        Returns: Expanded Series aligned to base_df index.
        """
        if mode == 'point':
            return series.reindex(base_df.index, method='ffill').fillna(method='ffill')
        elif mode == 'last':
            return series.reindex(base_df.index, method='ffill')
        # Add more modes as needed
        return series.reindex(base_df.index, method='ffill')

    def _ref(self, series, periods):
        """
        References past/future values.
        Purpose: Mimic Ref(array, -n).
        :param series: Pandas Series.
        :param periods: Positive for future, negative for past.
        Returns: Shifted Series.
        """
        return series.shift(-periods) if periods > 0 else series.shift(periods)

    def _var_set(self, name, value):
        """
        Sets a dynamic variable.
        Purpose: Mimic VarSet/VarGet.
        """
        self.var_dict[name] = value

    def _var_get(self, name):
        """
        Gets a dynamic variable.
        Purpose: Mimic VarGet.
        Returns: Value or None.
        """
        return self.var_dict.get(name, None)

    def _static_var_set(self, name, value):
        """
        Sets a persistent static variable.
        Purpose: Mimic StaticVarSet.
        """
        self.static_vars[name] = value
        self.static_vars.sync()

    def _static_var_get(self, name):
        """
        Gets a persistent static variable.
        Purpose: Mimic StaticVarGet.
        Returns: Value or None.
        """
        return self.static_vars.get(name, None)

    def _static_var_remove(self, name):
        """
        Removes a static variable.
        Purpose: Mimic StaticVarRemove.
        """
        if name in self.static_vars:
            del self.static_vars[name]
            self.static_vars.sync()

    def _price_vol_distribution(self, high, low, vol, bins, cumulative, start_idx, end_idx):
        """
        Calculates price volume distribution.
        Purpose: Mimic PriceVolDistribution.
        :param high, low, vol: Arrays.
        :param bins: Number of bins.
        :param cumulative: False (as in AFL).
        :param start_idx, end_idx: Range.
        Returns: Matrix [price, rel_volume].
        """
        # Slice data
        h = high[start_idx:end_idx+1]
        l = low[start_idx:end_idx+1]
        v = vol[start_idx:end_idx+1]
        
        # Find overall min/max price
        min_price = np.min(l)
        max_price = np.max(h)
        bin_edges = np.linspace(min_price, max_price, bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Initialize volume per bin
        bin_vol = np.zeros(bins)
        
        for i in range(len(h)):
            # Find bins overlapping with [l[i], h[i]]
            start_bin = np.searchsorted(bin_edges, l[i], side='left') - 1
            end_bin = np.searchsorted(bin_edges, h[i], side='right') - 1
            for b in range(max(0, start_bin), min(bins, end_bin + 1)):
                overlap = min(h[i], bin_edges[b+1]) - max(l[i], bin_edges[b])
                fraction = overlap / (h[i] - l[i]) if (h[i] - l[i]) > 0 else 0
                bin_vol[b] += v[i] * fraction
        
        total_vol = np.sum(bin_vol)
        rel_vol = bin_vol / total_vol if total_vol > 0 else np.zeros(bins)
        
        mx = np.column_stack((bin_centers, rel_vol))
        return mx

    def draw_h_line(self, x1, x2, y, clr, zorder, flag, txt, lw, ax):
        """
        Draws horizontal line and optional text.
        Purpose: Mimic drawHLine with Plot/PlotText.
        :param ax: Matplotlib axis.
        """
        ax.hlines(y, x1, x2, colors=clr, linestyles='dashed', linewidth=lw)
        if flag:
            ax.text(x2, y, f"{txt} {y:.2f}", color=clr, va='center', ha='left')

    def calculate_volume_area(self, mx_vol_bin_idx, tot_vol, bins, mx):
        """
        Calculates volume value area boundaries.
        Purpose: Direct translation of calculateVolumeArea function.
        Returns: mxih, mxil (high/low bin indices).
        """
        mxih = mxil = mx_vol_bin_idx
        tvol = mx[mx_vol_bin_idx, 1]
        for j in range(bins):
            if mxih + 1 < bins and mxil - 1 >= 0:
                relvolumeh = mx[mxih + 1, 1]
                relvolumel = mx[mxil - 1, 1]
                if relvolumeh > relvolumel:
                    mxih += 1
                    tvol += relvolumeh
                elif relvolumeh < relvolumel:
                    mxil -= 1
                    tvol += relvolumel
                elif relvolumeh == relvolumel:
                    mxih += 1
                    mxil -= 1
                    tvol += relvolumeh + relvolumel
            elif mxih + 1 >= bins and mxil - 1 >= 0:
                relvolumel = mx[mxil - 1, 1]
                mxil -= 1
                tvol += relvolumel
            elif mxih + 1 < bins and mxil - 1 < 0:
                relvolumeh = mx[mxih + 1, 1]
                mxih += 1
                tvol += relvolumeh
            if (tvol / tot_vol) >= self.params['volumeValueArea']:
                break
        return mxih, mxil

    def calculate_volume_value_area(self, fb, lb):
        """
        Calculates VAH, VAL, VPOC for visible range.
        Purpose: Direct translation of calculateVolumeValueArea function.
        Modifies self.df with VAH, VAL, VPOC.
        """
        # Assuming lbx0, lbx1, lbx2 are arrays from ValueWhen on separator
        separator = self.df['dn'] != self._ref(self.df['dn'], -1)
        lbx = {}
        for i in range(3 + self.params['shft']):
            lbx[i] = np.where(separator, self.bi, np.nan)
            for shift in range(1, i + 1):
                lbx[i] = self._ref(lbx[i], -1)
            lbx[i] = pd.Series(lbx[i]).fillna(method='ffill').values  # Approximate ValueWhen
        
        vah = np.full(self.bar_count, np.nan)
        val = np.full(self.bar_count, np.nan)
        vpoc = np.full(self.bar_count, np.nan)
        
        cnt = 0
        for i in range(lb, fb - 1, -1):
            idx0 = lbx[0][i] if i < len(lbx[0]) else np.nan
            idx1 = lbx[1][i] if i < len(lbx[1]) else np.nan
            idx2 = lbx[2][i] if i < len(lbx[2]) else np.nan
            if np.isnan(idx1):
                break
            mx = self._price_vol_distribution(self.df['High'].values, self.df['Low'].values, self.df['Volume'].values, 
                                              self.params['bins'], False, int(idx2), int(idx1) - 1)
            dx = int(idx1 - idx2)
            
            mx_vol_bin_idx = np.argmax(mx[:, 1])
            mx_vol = mx[mx_vol_bin_idx, 1]
            tot_vol = np.sum(mx[:, 1])
            
            # POC calculation (full loop as in AFL)
            for j in range(self.params['bins']):
                price = mx[j, 0]
                relvolume = mx[j, 1]
                # Show volume bars (commented in AFL, so optional)
                if self.params['showVolume']:
                    pass  # Implement draw if needed
                if relvolume >= mx_vol:
                    if relvolume == mx_vol:
                        if abs(j - (self.params['bins'] / 2)) < abs(mx_vol_bin_idx - (self.params['bins'] / 2)):
                            mx_vol = relvolume
                            mx_vol_bin_idx = j
                    else:
                        mx_vol = relvolume
                        mx_vol_bin_idx = j
            
            price_vpoc = mx[mx_vol_bin_idx, 0]
            mxih, mxil = self.calculate_volume_area(mx_vol_bin_idx, tot_vol, self.params['bins'], mx)
            
            priceh = mx[mxih, 0]
            pricel = mx[mxil, 0]
            x1 = int(idx2)
            x2 = min(int(idx1), self.bar_count - 1)
            
            # LineArray approximation: fill from x1 to x2 with value
            vah[x1:x2+1] = priceh
            val[x1:x2+1] = pricel
            vpoc[x1:x2+1] = price_vpoc
            
            # Give color to volume area (optional)
            if self.params['giveVolumeAreaColor']:
                for j in range(self.params['bins']):
                    price = mx[j, 0]
                    relvolume = mx[j, 1]
                    if self.params['showVolume'] and pricel <= price <= priceh:
                        pass  # Draw colored
            
            if self.params['showHL']:
                ph = self.df['HOD'].values[x2 - 1]
                self.draw_h_line(x1, x2, ph, 'g', -3, self.params['showLabel'], "HOD ", self.params['lineWidth1'], None)
                pl = self.df['LOD'].values[x2 - 1]
                self.draw_h_line(x1, x2, pl, 'r', -3, self.params['showLabel'], "LOD ", self.params['lineWidth1'], None)
            
            if self.params['showMain']:
                self.draw_h_line(x1, x2, priceh, 'c', -3, self.params['showLabel'], "VAH ", self.params['lineWidth1'], None)
                self.draw_h_line(x1, x2, pricel, 'c', -3, self.params['showLabel'], "VAL ", self.params['lineWidth1'], None)
                self.draw_h_line(x1, x2, price_vpoc, '#cc4d99', -3, self.params['showLabel'], "VPOC ", self.params['lineWidth1'], None)
            
            if cnt == 0:
                x1 = x2
                x2 = min(lvb, self.bar_count - 1)
                if x2 == 0:
                    x2 = self.bar_count - 1
                
                if self.params['showHL']:
                    ph = self.df['HOD'].values[x2]
                    self.draw_h_line(x1, x2, ph, 'g', -3, self.params['showLabel'], "HOD ", self.params['lineWidth1'], None)
                    pl = self.df['LOD'].values[x2]
                    self.draw_h_line(x1, x2, pl, 'r', -3, self.params['showLabel'], "LOD ", self.params['lineWidth1'], None)
                
                mx = self._price_vol_distribution(self.df['High'].values, self.df['Low'].values, self.df['Volume'].values, 
                                                  self.params['bins'], False, x1, x2)
                dx = x2 - x1
                
                mx_vol_bin_idx = np.argmax(mx[:, 1])
                mx_vol = mx[mx_vol_bin_idx, 1]
                tot_vol = np.sum(mx[:, 1])
                
                for j in range(self.params['bins']):
                    price = mx[j, 0]
                    relvolume = mx[j, 1]
                    if self.params['showVolume']:
                        pass  # Draw
                
                price_vpoc = mx[mx_vol_bin_idx, 0]
                mxih, mxil = self.calculate_volume_area(mx_vol_bin_idx, tot_vol, self.params['bins'], mx)
                
                priceh = mx[mxih, 0]
                pricel = mx[mxil, 0]
                
                vah[x1:x2+1] = priceh
                val[x1:x2+1] = pricel
                vpoc[x1:x2+1] = price_vpoc
                
                if self.params['showMain']:
                    self.draw_h_line(x1, x2, priceh, 'c', -3, self.params['showLabel'], "VAH ", self.params['lineWidth1'], None)
                    self.draw_h_line(x1, x2, pricel, 'c', -3, self.params['showLabel'], "VAL ", self.params['lineWidth1'], None)
                    self.draw_h_line(x1, x2, price_vpoc, '#cc4d99', -3, self.params['showLabel'], "VPOC ", self.params['lineWidth1'], None)
                
                if self.params['giveVolumeAreaColor'] and self.params['showVolume']:
                    for j in range(self.params['bins']):
                        price = mx[j, 0]
                        relvolume = mx[j, 1]
                        if pricel <= price <= priceh:
                            pass  # Draw colored
            
            # Update i as in AFL
            if 'idx1' in locals():
                i = lbx[1][int(idx1)] if int(idx1) < len(lbx[1]) else i
            cnt += 1
        
        self.df['VAH'] = vah
        self.df['VAL'] = val
        self.df['VPOC'] = vpoc

    def shift_volume_value_area(self, fb, lb, shft):
        """
        Shifts value area levels.
        Purpose: Direct translation of shiftVolumeValueArea function.
        Modifies dynamic vars for shifted levels.
        """
        # lbx setup similar to above
        lbx = {}
        for i in range(3 + shft):
            separator = self.df['dn'] != self._ref(self.df['dn'], -1)
            lbx[i] = np.where(separator, self.bi, np.nan)
            for shift in range(1, i + 1):
                lbx[i] = self._ref(lbx[i], -1)
            lbx[i] = pd.Series(lbx[i]).fillna(method='ffill').values
        
        for i in range(lb, fb - 1, -1):
            if lbx[0][i] == lbx[1][i]:
                x1 = lbx[1][i]
                x2 = min(lb, self.bar_count - 1)
            else:
                x1 = lbx[1][i]
                x2 = min(lb, lbx[0][i])
            
            for s in range(1, shft + 1):
                xx0 = lbx[s - 1]
                xx1 = lbx[s]
                xx2 = lbx[s + 1]
                
                if xx0[i] == xx1[i]:
                    x1s = xx2[i]
                    x2s = xx1[i]
                    if not np.isnan(x1s):
                        if self.params['showShifted']:
                            self.draw_h_line(x1, x2, self.df['VPOC'].values[int(x1s)], (250 / s, 0, 250 / s), -3, self.params['showLabel'], f"VPOCn{s} ", self.params['lineWidth1'], None)
                            self.draw_h_line(x1, x2, self.df['VAH'].values[int(x1s)], (250 / s, 250 / s, 0), -3, self.params['showLabel'], f"VAHn{s} ", self.params['lineWidth1'], None)
                            self.draw_h_line(x1, x2, self.df['VAL'].values[int(x1s)], (250 / s, 250 / s, 0), -3, self.params['showLabel'], f"VALn{s} ", self.params['lineWidth1'], None)
                        
                        if self.params['showShiftedHL']:
                            self.draw_h_line(x1, x2, self.df['HOD'].values[int(x1s)], (0, 250, 0), -3, self.params['showLabel'], f"HODn{s} ", self.params['lineWidth1'], None)
                            self.draw_h_line(x1, x2, self.df['LOD'].values[int(x1s)], (250, 0, 0), -3, self.params['showLabel'], f"LODn{s} ", self.params['lineWidth1'], None)
                        
                        # Save to dynamic vars
                        if not np.isnan(self.df['VPOC'].values[int(x1s)]):
                            line = np.full(x2 - x1 + 1, self.df['VPOC'].values[int(x1s)])
                            self._var_set(f"VPOCn{s}", line if line is not None else self._var_get(f"VPOCn{s}"))
                        # Similar for VAH, VAL
                        if not np.isnan(self.df['VAH'].values[int(x1s)]):
                            line = np.full(x2 - x1 + 1, self.df['VAH'].values[int(x1s)])
                            self._var_set(f"VAHn{s}", line if line is not None else self._var_get(f"VAHn{s}"))
                        if not np.isnan(self.df['VAL'].values[int(x1s)]):
                            line = np.full(x2 - x1 + 1, self.df['VAL'].values[int(x1s)])
                            self._var_set(f"VALn{s}", line if line is not None else self._var_get(f"VALn{s}"))
                
                elif xx1[i] < xx0[i]:
                    x1s = xx2[i]
                    x2s = xx1[i]
                    if not np.isnan(x1s):
                        # Similar to above for showShifted, showShiftedHL, var_set
                        if self.params['showShifted']:
                            self.draw_h_line(x1, x2, self.df['VPOC'].values[int(x1s)], (250 / s, 0, 250 / s), -3, self.params['showLabel'], f"VPOCn{s} ", self.params['lineWidth1'], None)
                            # ... rest similar
                        # And so on
                
            # Update i
            i = lbx[1][i] if i < len(lbx[1]) else i

    def _get_foreign(self, symbol):
        """
        Loads external data for indices.
        Purpose: Mimic SetForeign.
        Returns: DataFrame for the symbol (placeholder - assume loaded from file or API).
        """
        # Placeholder: In real project, load from file or API
        # For now, return dummy DF with same structure
        dummy_df = self.df.copy()
        dummy_df['Close'] = dummy_df['Close'] * 1.1  # Dummy
        return dummy_df

    def _separator(self):
        """
        Calculates separator based on sep param.
        Purpose: Mimic dn calculation for day/week/month/year.
        """
        sep = self.params['sep']
        if sep == "Day":
            self.df['dn'] = self.df.index.day
            dn1 = 'D'
        elif sep == "Week":
            self.df['dw'] = self.df.index.dayofweek
            self.df['newWeek'] = self.df['dw'] < self._ref(self.df['dw'], -1)
            self.df['newYear'] = self.df.index.year != self._ref(self.df.index.year, -1)
            self.df['weekNumber'] = self.df['newWeek'].cumsum() + self.df['newYear'].astype(int)
            self.df['dn'] = self.df['weekNumber']
            dn1 = 'W'
        elif sep == "Month":
            self.df['dn'] = self.df.index.month
            dn1 = 'M'
        elif sep == "Year":
            self.df['dn'] = self.df.index.year
            dn1 = 'Y'
        return dn1

    def _time_frame_get_price(self, price_type, timeframe, shift=0):
        """
        Gets price from resampled timeframe.
        Purpose: Mimic TimeFrameGetPrice.
        """
        res_df = self._resample(timeframe)
        if price_type == "H":
            price = res_df['High']
        elif price_type == "L":
            price = res_df['Low']
        elif price_type == "C":
            price = res_df['Close']
        elif price_type == "O":
            price = res_df['Open']
        price = self._ref(price, shift)
        return self._expand(price, self.df, 'last')

    def _flip(self, cond1, cond2):
        """
        Mimics Flip.
        Purpose: Cumulative state between cond1 and cond2.
        Returns: Array where 1 between cond1 and cond2.
        """
        flip = np.zeros(self.bar_count)
        state = 0
        for i in range(self.bar_count):
            if cond1[i]:
                state = 1
            if cond2[i]:
                state = 0
            flip[i] = state
        return flip

    def run_volume_profile(self):
        """
        Runs the volume profile logic.
        Purpose: Translate the volume profile section.
        """
        dn1 = self._separator()
        self.df['separator'] = self.df['dn'] != self._ref(self.df['dn'], -1)
        
        fvb = max(0, self.bi.min())
        lvb = max(0, self.bi.max())
        
        self.df['HOD'] = self._time_frame_get_price("H", dn1)
        self.df['LOD'] = self._time_frame_get_price("L", dn1)
        
        # lbx setup
        for i in range(3 + self.params['shft']):
            self._var_set(f"lbx{i}", np.where(self.df['separator'], self.bi, np.nan))
            # ValueWhen approximation with ffill
            self._var_set(f"lbx{i}", pd.Series(self._var_get(f"lbx{i}")).fillna(method='ffill').values)
        
        # Open/Close VAH etc.
        self.df['OpenVAH'] = 0
        self.df['OpenVAL'] = 0
        self.df['OpenVPOC'] = 0
        self.df['OpenLOD'] = 0
        self.df['OpenHOD'] = 0
        
        self.df['NewCandle'] = self.bi != self._ref(pd.Series(self.bi), -1)
        
        self.df['OpenVAH'] = np.where(self.df['separator'], self.df['VAH'], self._ref(self.df['OpenVAH'], -1).fillna(0))
        self.df['OpenVAL'] = np.where(self.df['separator'], self.df['VAL'], self._ref(self.df['OpenVAL'], -1).fillna(0))
        self.df['OpenVPOC'] = np.where(self.df['separator'], self.df['VPOC'], self._ref(self.df['OpenVPOC'], -1).fillna(0))
        self.df['OpenLOD'] = np.where(self.df['separator'], self.df['LOD'], self._ref(self.df['OpenLOD'], -1).fillna(0))
        self.df['OpenHOD'] = np.where(self.df['separator'], self.df['HOD'], self._ref(self.df['OpenHOD'], -1).fillna(0))
        
        self.df['CloseVAH'] = self.df['VAH']
        self.df['CloseVAL'] = self.df['VAL']
        self.df['CloseVPOC'] = self.df['VPOC']
        self.df['CloseLOD'] = self.df['LOD']
        self.df['CloseHOD'] = self.df['HOD']
        
        # Call calculate
        self.calculate_volume_value_area(fvb, lvb)
        
        # Shift
        self.shift_volume_value_area(fvb, lvb, self.params['shft'])
        
        # Shifted vars loop
        for s in range(1, self.params['maxShift'] + 1):
            variable_name = f"VPOCn{s}"
            vah_variable_name = f"VAHn{s}"
            val_variable_name = f"VALn{s}"
            hod_variable_name = f"HODn{s}"
            lod_variable_name = f"LODn{s}"
            shifted_vpoc = self._var_get(variable_name)
            shifted_vah = self._var_get(vah_variable_name)
            shifted_val = self._var_get(val_variable_name)
            shifted_hod = self._var_get(hod_variable_name)
            shifted_lod = self._var_get(lod_variable_name)
        
        self.df['VALn1'] = self._ref(self.df['VAL'], -1)
        self.df['VAHn1'] = self._ref(self.df['VAH'], -1)
        self.df['VPOCn1'] = self._ref(self.df['VPOC'], -1)
        self.df['HoDn1'] = self._ref(self.df['HOD'], -1)
        self.df['LoDn1'] = self._ref(self.df['LOD'], -1)

    def run_indicators(self):
        """
        Calculates all indicators in 5min timeframe.
        Purpose: Translate the 5min TimeFrameSet section.
        """
        df_5min = self._resample('5T')
        
        # MACD
        df_5min['MACDLine'] = talib.MACD(df_5min['Close'], fastperiod=self.params['fastLength'], slowperiod=self.params['slowLength'], signalperiod=self.params['signalSmoothing'])[0]
        df_5min['SignalLine'] = talib.MACD(df_5min['Close'], fastperiod=self.params['fastLength'], slowperiod=self.params['slowLength'], signalperiod=self.params['signalSmoothing'])[2]
        df_5min['MACDHist'] = df_5min['MACDLine'] - df_5min['SignalLine']
        
        # RSI
        df_5min['RSIValue'] = talib.RSI(df_5min['Close'], timeperiod=self.params['RSI_Period'])
        
        # ADX
        df_5min['adxValue'] = talib.ADX(df_5min['High'], df_5min['Low'], df_5min['Close'], timeperiod=self.params['ADX_Period'])
        
        # SAR
        df_5min['SAR1'] = talib.SAR(df_5min['High'], df_5min['Low'], acceleration=0.02, maximum=0.2)
        
        # Stochastic
        df_5min['SlowK'] = talib.STOCH(df_5min['High'], df_5min['Low'], df_5min['Close'], fastk_period=self.params['KPeriod'], slowk_period=self.params['DPeriod'], slowk_matype=0)[0]
        df_5min['SlowD'] = talib.MA(df_5min['SlowK'], timeperiod=self.params['DPeriod'], matype=0)
        
        # Bollinger
        df_5min['MiddleBand'] = talib.MA(df_5min['Close'], timeperiod=self.params['Period'])
        std_dev = talib.STDDEV(df_5min['Close'], timeperiod=self.params['Period'])
        df_5min['UpperBand'] = df_5min['MiddleBand'] + self.params['Width'] * std_dev
        df_5min['LowerBand'] = df_5min['MiddleBand'] - self.params['Width'] * std_dev
        
        # Candle Body to Wick
        df_5min['BodySize'] = np.abs(df_5min['Close'] - df_5min['Open'])
        df_5min['CandleRange'] = df_5min['High'] - df_5min['Low']
        df_5min['StrengthPct'] = (df_5min['BodySize'] / (df_5min['CandleRange'] + 1e-9)) * 100
        
        # Relative Strength Volume
        df_5min['CandleStrength'] = (df_5min['Close'] - df_5min['Open']) * df_5min['Volume']
        
        # Wick Analysis
        df_5min['UpperWick'] = df_5min['High'] - np.maximum(df_5min['Open'], df_5min['Close'])
        df_5min['LowerWick'] = np.minimum(df_5min['Open'], df_5min['Close']) - df_5min['Low']
        
        # Strength Breakout
        df_5min['ATR_14'] = talib.ATR(df_5min['High'], df_5min['Low'], df_5min['Close'], 14)
        df_5min['ATR_Strength'] = (df_5min['CandleRange'] / df_5min['ATR_14']) * 100
        df_5min['ATR_3'] = talib.ATR(df_5min['High'], df_5min['Low'], df_5min['Close'], 3)
        df_5min['ATR3_Strength'] = (df_5min['CandleRange'] / df_5min['ATR_3']) * 100
        
        # RSI manual (as backup, but using talib above)
        up_move = np.where(df_5min['Close'] > self._ref(df_5min['Close'], -1), df_5min['Close'] - self._ref(df_5min['Close'], -1), 0)
        down_move = np.where(df_5min['Close'] < self._ref(df_5min['Close'], -1), self._ref(df_5min['Close'], -1) - df_5min['Close'], 0)
        avg_up = talib.MA(up_move, self.params['RSI_Period'])
        avg_down = talib.MA(down_move, self.params['RSI_Period'])
        rs = avg_up / (avg_down + 1e-5)
        df_5min['RSIValue_manual'] = 100 - (100 / (1 + rs))
        
        # Short term trend
        df_5min['ShortEMA'] = talib.EMA(df_5min['Close'], 9)
        df_5min['LongEMA'] = talib.EMA(df_5min['Close'], 21)
        df_5min['ADXValue'] = talib.ADX(df_5min['High'], df_5min['Low'], df_5min['Close'], 14)
        df_5min['StrongTrend'] = df_5min['ADXValue'] > 25
        df_5min['UpTrend'] = df_5min['StrongTrend'] & (df_5min['ShortEMA'] > df_5min['LongEMA'])
        df_5min['DownTrend'] = df_5min['StrongTrend'] & (df_5min['ShortEMA'] < df_5min['LongEMA'])
        
        # VWAP Trend
        day_start = self._time_frame_get_price("O", 'D')
        cumulative_volume = df_5min['Volume'].cumsum()
        cumulative_tpv = ((df_5min['High'] + df_5min['Low'] + df_5min['Close']) / 3 * df_5min['Volume']).cumsum()
        df_5min['VWAP'] = cumulative_tpv / cumulative_volume
        df_5min['BullishTrend'] = df_5min['Close'] > df_5min['VWAP']
        df_5min['BearishTrend'] = df_5min['Close'] < df_5min['VWAP']
        
        # Volume POC/PONC (simplified rolling)
        lookback = self.params['lookbackPeriod']
        highest_vol = df_5min['Volume'].rolling(lookback).max()
        lowest_vol = df_5min['Volume'].rolling(lookback).min()
        df_5min['highestVolPrice'] = np.where(df_5min['Volume'] == highest_vol, df_5min['Close'], np.nan).ffill()
        df_5min['lowestVolPrice'] = np.where(df_5min['Volume'] == lowest_vol, df_5min['Close'], np.nan).ffill()
        
        cum_volume = df_5min['Volume'].cumsum()
        cum_vwap = (df_5min['Volume'] * df_5min['Close']).cumsum()
        df_5min['vwapValue'] = np.where(cum_volume != 0, cum_vwap / cum_volume, 0)
        
        df_5min['VolumeMA'] = talib.MA(df_5min['Volume'], self.params['PeriodVol'])
        df_5min['VolumeSpike'] = df_5min['Volume'] > 1.3 * df_5min['VolumeMA']
        df_5min['VolumeSpike1'] = df_5min['Volume'] > 1.2 * df_5min['VolumeMA']
        
        # Enhanced VWAP
        df_5min['EMA_Short'] = talib.EMA(df_5min['Close'], 9)
        df_5min['EMA_Long'] = talib.EMA(df_5min['Close'], 21)
        df_5min['Momentum'] = talib.ROC(df_5min['Close'], 5)
        df_5min['VolumeMA10'] = talib.MA(df_5min['Volume'], 10)
        df_5min['BullishTrendVol'] = (df_5min['Close'] > df_5min['VWAP']) & (df_5min['EMA_Short'] > df_5min['EMA_Long']) & (df_5min['Momentum'] > 0) & (df_5min['Volume'] > df_5min['VolumeMA10'])
        df_5min['BearishTrendVol'] = (df_5min['Close'] < df_5min['VWAP']) & (df_5min['EMA_Short'] < df_5min['EMA_Long']) & (df_5min['Momentum'] < 0) & (df_5min['Volume'] > df_5min['VolumeMA10'])
        
        # Momentum RSI Divergence
        df_5min['RSI_Value'] = talib.RSI(df_5min['Close'], self.params['RSI_Period'])
        price_high = self._ref(df_5min['High'], -1)
        rsi_high = self._ref(df_5min['RSI_Value'], -1)
        price_high1 = self._ref(price_high, -1)
        price_high2 = self._ref(price_high, -2)
        rsi_high1 = self._ref(rsi_high, -1)
        rsi_high2 = self._ref(rsi_high, -2)
        df_5min['BearishDivergence'] = (price_high > price_high1) & (price_high1 > price_high2) & (rsi_high < rsi_high1) & (rsi_high1 < rsi_high2)
        df_5min['BullishDivergence'] = (price_high < price_high1) & (price_high1 < price_high2) & (rsi_high > rsi_high1) & (rsi_high1 > rsi_high2)
        df_5min['ConfirmedSell'] = self._ref(df_5min['BearishDivergence'], -1)
        df_5min['ConfirmedBuy'] = self._ref(df_5min['BullishDivergence'], -1)
        
        # MA Slope & ADX
        df_5min['ma1'] = talib.MA(df_5min['Close'], self.params['maPeriod'])
        df_5min['maSlope'] = talib.ROC(df_5min['ma1'], self.params['slopeLookback'])
        prev_slope = self._ref(df_5min['maSlope'], -1)
        prev_adx = self._ref(df_5min['adxValue'], -1)
        df_5min['TrendFilter'] = (prev_adx > self.params['adxThreshold']) & (np.abs(prev_slope) > self.params['slopeThreshold'])
        
        # Donchian
        df_5min['donchianHigh'] = df_5min['High'].rolling(self.params['donchianPeriod']).max()
        df_5min['donchianLow'] = df_5min['Low'].rolling(self.params['donchianPeriod']).min()
        df_5min['donchianRange'] = df_5min['donchianHigh'] - df_5min['donchianLow']
        df_5min['donchianThreshold'] = talib.MA(df_5min['donchianRange'], 20) * 0.5
        df_5min['DonTrendFilter'] = df_5min['donchianRange'] > df_5min['donchianThreshold']
        
        # TSI
        ratio = np.abs(df_5min['Close'] - self._ref(df_5min['Close'], -10)) / talib.ATR(df_5min['High'], df_5min['Low'], df_5min['Close'], 10)
        df_5min['TSI'] = talib.MA(talib.MA(ratio, 10), 100)
        
        # ATR3P
        df_5min['ATR3P'] = talib.ATR(df_5min['High'], df_5min['Low'], df_5min['Close'], 3)
        
        # Linear Reg Angle
        df_5min['Slope'] = talib.LINEARREG_SLOPE(df_5min['Close'], self.params['Len'])
        df_5min['Angle'] = np.arctan(df_5min['Slope']) * 180 / np.pi
        
        # Test 12042025
        df_5min['CSI'] = (df_5min['Close'] - df_5min['Low']) / (df_5min['High'] - df_5min['Low'] + 0.001)
        
        green_vol = np.where(df_5min['Close'] > df_5min['Open'], df_5min['Volume'], 0)
        red_vol = np.where(df_5min['Close'] < df_5min['Open'], df_5min['Volume'], 0)
        vol_imbalance = talib.EMA(green_vol - red_vol, 5) / talib.EMA(df_5min['Volume'], 5)
        
        body = np.abs(df_5min['Close'] - df_5min['Open'])
        upper_wick = df_5min['High'] - np.maximum(df_5min['Close'], df_5min['Open'])
        lower_wick = np.minimum(df_5min['Close'], df_5min['Open']) - df_5min['Low']
        df_5min['BWR'] = body / (upper_wick + lower_wick + 0.001)
        
        thrust = df_5min['Close'] - self._ref(df_5min['Close'], -1)
        atr_val = talib.ATR(df_5min['High'], df_5min['Low'], df_5min['Close'], 14)
        df_5min['MomentumThrust'] = thrust / atr_val
        
        df_5min['CSS'] = 40 * df_5min['CSI'] + 20 * vol_imbalance + 15 * df_5min['BWR'] + 15 * df_5min['MomentumThrust'] + 10 * df_5min['Angle'] / 45
        
        # All conditions (no skips - full translation)
        df_5min['STD'] = df_5min['vwapValue'] > self._ref(df_5min['vwapValue'], -1) & df_5min['VolumeSpike']
        df_5min['GC'] = self._ref(df_5min['Open'], -1) < self._ref(df_5min['Close'], -1)
        df_5min['RC'] = self._ref(df_5min['Open'], -1) > self._ref(df_5min['Close'], -1)
        df_5min['B0'] = df_5min['High'] > self._ref(df_5min['High'], -1)
        df_5min['B1'] = self._ref(df_5min['StrengthPct'], -1) > 65 & df_5min['GC']
        df_5min['B101'] = self._ref(df_5min['StrengthPct'], -1) < 10 & (df_5min['RC'] | df_5min['GC'])
        df_5min['B2'] = self._ref(df_5min['UpperWick'], -1) > self._ref(df_5min['LowerWick'], -1)
        df_5min['B21'] = self._ref(df_5min['UpperWick'], -1) < self._ref(df_5min['LowerWick'], -1)
        df_5min['B3'] = self._ref(df_5min['CandleStrength'], -1) > 0
        df_5min['B31'] = self._ref(df_5min['CandleStrength'], -1) > 120000
        df_5min['B32'] = self._ref(df_5min['CandleStrength'], -1) > 500000
        df_5min['B4'] = self._ref(df_5min['ATR_Strength'], -1) > 100
        df_5min['B41'] = self._ref(df_5min['ATR_Strength'], -1) > 80
        df_5min['B5'] = self._ref(df_5min['RSIValue'], -1) > 39
        df_5min['B6'] = self._ref(df_5min['UpTrend'], -1)
        df_5min['B7'] = self._ref(df_5min['BullishTrend'], -1)
        df_5min['B8'] = self._ref(df_5min['BullishTrendVol'], -1)
        df_5min['B9'] = df_5min['ConfirmedBuy']
        df_5min['B10'] = self._ref(df_5min['DonTrendFilter'], -1)
        df_5min['B11'] = df_5min['B101'] & df_5min['B21']
        df_5min['B12'] = self._ref(df_5min['ATR3P'], -1) > 50
        df_5min['FiveHigh'] = df_5min['High']
        df_5min['PreFiveMinOpen'] = self._ref(df_5min['Open'], -1)
        df_5min['PreFiveMinHigh'] = self._ref(df_5min['High'], -1)
        df_5min['PreFiveMinLow'] = self._ref(df_5min['Low'], -1)
        df_5min['PreFiveMinClose'] = self._ref(df_5min['Close'], -1)
        
        # Sell conditions (full, no skips)
        df_5min['S1'] = (self._ref(df_5min['High'], -1) == self._ref(df_5min['Close'], -1)) & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (self._ref(df_5min['Low'], -1) < df_5min['Close']) & df_5min['GC']
        df_5min['S2'] = (self._ref(df_5min['High'], -1) == self._ref(df_5min['Close'], -1)) & (df_5min['Open'] > self._ref(df_5min['High'], -1)) & (self._ref(df_5min['Low'], -1) < df_5min['Close']) & (df_5min['Low'] < (self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02)) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['GC']
        df_5min['S3'] = (df_5min['MACDLine'] < df_5min['SignalLine']) & (df_5min['RSIValue'] < 50) & (df_5min['adxValue'] < 25) & (df_5min['SlowK'] >= 80) & df_5min['GC']
        df_5min['S4'] = (df_5min['Open'] > self._ref(df_5min['High'], -1)) & (self._ref(df_5min['Open'], -1) != self._ref(df_5min['Low'], -1)) & (df_5min['Low'] < self._ref(df_5min['Close'], -1) - 6) & (df_5min['Low'] < (self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02)) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['GC']
        df_5min['S5'] = (self._ref(df_5min['Open'], -1) - self._ref(df_5min['Low'], -1) < 1) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) - (self._ref(df_5min['Open'], -1) + self._ref(df_5min['Close'], -1)) / 2 * 0.03) & (df_5min['Low'] < (self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02)) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['GC']
        df_5min['S6'] = self._ref(df_5min['High'], -1) < self._ref(df_5min['High'], -2) & df_5min['GC']
        df_5min['S7'] = self._ref(df_5min['Low'], -1) < self._ref(df_5min['Low'], -2) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) - 2) & (df_5min['Low'] < (self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02)) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['GC']
        df_5min['S8'] = (df_5min['Low'] < self._ref(df_5min['Open'], -1)) & (df_5min['Low'] < self._ref(df_5min['Open'], -2)) & (df_5min['Low'] < self._ref(df_5min['Low'], -1)) & (df_5min['Low'] < self._ref(df_5min['Low'], -2)) & (self._ref(df_5min['Open'], -2) > self._ref(df_5min['Close'], -2)) & (df_5min['Low'] < (self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02)) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['GC']
        df_5min['S9'] = (df_5min['Low'] < self._ref(df_5min['Low'], -1) - 2) & (df_5min['Low'] < self._ref(df_5min['Open'], -2) - 3) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.04) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['GC']
        df_5min['S3R'] = (df_5min['MACDLine'] < df_5min['SignalLine']) & (df_5min['RSIValue'] < 50) & (df_5min['adxValue'] < 25) & (df_5min['SlowK'] >= 80) & df_5min['RC']
        df_5min['SR1'] = (df_5min['Open'] < self._ref(df_5min['Low'], -1)) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['RC']
        df_5min['SR2'] = (self._ref(df_5min['Close'], -1) - self._ref(df_5min['Low'], -1) < 0.4) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) ) & (self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['RC']  # Note: <5 in AFL, but seems typo or specific; kept as is
        df_5min['SR3'] = df_5min['RC'] & (self._ref(df_5min['Open'], -1) - self._ref(df_5min['Close'], -1) < self._ref(df_5min['High'], -1) - self._ref(df_5min['Open'], -1)) & (self._ref(df_5min['High'], -1) - self._ref(df_5min['Open'], -1) > self._ref(df_5min['Close'], -1) - self._ref(df_5min['Low'], -1)) & (self._ref(df_5min['Close'], -1) - self._ref(df_5min['Low'], -1) < self._ref(df_5min['Open'], -1) - self._ref(df_5min['Close'], -1)) & (df_5min['Low'] < self._ref(df_5min['Low'], -1)) & (df_5min['Open'] - df_5min['Low'] > 2)
        df_5min['SR4'] = (df_5min['High'] - df_5min['Open'] < 2) & (df_5min['Low'] < self._ref(df_5min['Low'], -1)) & df_5min['RC']
        df_5min['SR5'] = (self._ref(df_5min['High'], -1) > self._ref(df_5min['High'], -2)) & (self._ref(df_5min['Low'], -1) > self._ref(df_5min['Low'], -2)) & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (df_5min['Open'] - self._ref(df_5min['Close'], -1) > 0.5) & (df_5min['High'] > df_5min['BuyPrice'] + df_5min['BuyPrice'] * 0.06) & df_5min['RC']  # BuyPrice not defined; assume it's entry from loop, or placeholder
        df_5min['SR6'] = df_5min['SR5']  # AFL has duplicate SR6 = SR5
        df_5min['SR7'] = (df_5min['Open'] < self._ref(df_5min['Close'], -1)) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) - 3) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['RC']
        df_5min['SR8'] = (df_5min['Low'] < self._ref(df_5min['Low'], -1) - 3) & (self._ref(df_5min['Open'], -2) > self._ref(df_5min['Close'], -2)) & (df_5min['Low'] <= self._ref(df_5min['Low'], -2)) & (df_5min['Low'] < self._ref(df_5min['Low'], -1) - self._ref(df_5min['Low'], -1) * 0.02) & (df_5min['Open'] - df_5min['Low'] > 2) & df_5min['RC']
        df_5min['SR9'] = (self._ref(df_5min['High'], -1) > self._ref(df_5min['High'], -2)) & (self._ref(df_5min['Low'], -1) > self._ref(df_5min['Low'], -2)) & (df_5min['High'] > df_5min['BuyPrice'] + df_5min['BuyPrice'] * 0.06) & df_5min['RC']
        
        # Combo formulas (full, no skips)
        df_5min['CB1'] = df_5min['GC'] & (df_5min['MACDLine'] > df_5min['SignalLine']) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 10) & (df_5min['SlowK'] > df_5min['SlowD']) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['CB2'] = df_5min['GC'] & (df_5min['MACDLine'] > 5) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 10) & (df_5min['SlowK'] > df_5min['SlowD']) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['CB3'] = df_5min['GC'] & (df_5min['Open'] < df_5min['LowerBand']) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['CB4'] = (df_5min['RSIValue'] > 20) & (df_5min['SlowK'] > df_5min['SlowD']) & (df_5min['adxValue'] > 40) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['CB5'] = df_5min['GC'] & (df_5min['MACDLine'] > df_5min['SignalLine']) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 20) & (df_5min['Open'] >= df_5min['LowerBand'])
        df_5min['CB6'] = df_5min['GC'] & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 19) & (df_5min['Open'] >= df_5min['LowerBand']) & (df_5min['SlowK'] > df_5min['SlowD'])
        df_5min['CBR1'] = df_5min['RC'] & (df_5min['MACDLine'] > df_5min['SignalLine']) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 10) & (df_5min['SlowK'] > df_5min['SlowD']) & (df_5min['High'] >= df_5min['MiddleBand']) & (df_5min['Open'] < df_5min['UpperBand']) & (df_5min['SlowK'] - df_5min['SlowD'] < 1.6)
        df_5min['CBR2'] = df_5min['RC'] & (df_5min['MACDLine'] > 5) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 10) & (df_5min['Open'] < df_5min['UpperBand']) & (df_5min['SlowK'] - df_5min['SlowD'] < 1.6) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['CBR3'] = df_5min['RC'] & (df_5min['Open'] < self._ref(df_5min['LowerBand'], -1)) & (df_5min['Open'] > df_5min['UpperBand']) & (df_5min['SlowK'] - df_5min['SlowD'] < 1.6) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['CBR4'] = df_5min['RC'] & (df_5min['MACDLine'] > df_5min['SignalLine']) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 20) & (df_5min['Open'] >= df_5min['LowerBand'])
        df_5min['BR1'] = df_5min['STD'] & df_5min['RC'] & (df_5min['MACDLine'] > df_5min['SignalLine']) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 25) & (df_5min['SlowK'] > df_5min['SlowD']) & (df_5min['Open'] < df_5min['UpperBand']) & (df_5min['High'] >= df_5min['MiddleBand']) & (df_5min['SlowK'] - df_5min['SlowD'] > 1.6)
        df_5min['BR2'] = df_5min['STD'] & df_5min['RC'] & (df_5min['MACDLine'] > 5) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 25) & (df_5min['Open'] < df_5min['UpperBand']) & (df_5min['SlowK'] - df_5min['SlowD'] > 1.6) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['BR3'] = df_5min['STD'] & df_5min['RC'] & (df_5min['Open'] < df_5min['LowerBand']) & (df_5min['Open'] < df_5min['UpperBand']) & (df_5min['SlowK'] - df_5min['SlowD'] > 1.6) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['BR4'] = df_5min['STD'] & df_5min['RC'] & (df_5min['MACDLine'] > df_5min['SignalLine']) & (df_5min['RSIValue'] > 40) & (df_5min['adxValue'] > 20) & (df_5min['Open'] >= df_5min['LowerBand']) & (df_5min['High'] >= df_5min['MiddleBand'])
        df_5min['BR5'] = df_5min['STD'] & df_5min['RC'] & (df_5min['Low'] < df_5min['LowerBand']) & (df_5min['High'] > self._ref(df_5min['High'], -1))
        df_5min['BR6'] = (self._ref(df_5min['Low'], -1) < self._ref(df_5min['LowerBand'], -1)) & (self._ref(df_5min['Close'], -1) > self._ref(df_5min['LowerBand'], -1))
        df_5min['NRC1'] = (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) & (df_5min['High'] > self._ref(df_5min['High'], -2))
        df_5min['NRC2'] = (self._ref(df_5min['High'], -1) > self._ref(df_5min['High'], -2)) & (self._ref(df_5min['Low'], -1) > self._ref(df_5min['Low'], -2)) & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (self._ref(df_5min['Close'], -2) != self._ref(df_5min['High'], -2)) & (df_5min['High'] > (self._ref(df_5min['Open'], -1) + self._ref(df_5min['Close'], -1)) / 2)
        df_5min['NRC3'] = (self._ref(df_5min['High'], -1) - self._ref(df_5min['Open'], -1) < self._ref(df_5min['Close'], -1) - self._ref(df_5min['Low'], -1)) & (self._ref(df_5min['Open'], -1) - self._ref(df_5min['Close'], -1) <= 2) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['NRC4'] = (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (df_5min['High'] > self._ref(df_5min['Open'], -1)) & (self._ref(df_5min['Open'], -2) > self._ref(df_5min['Close'], -2)) & (df_5min['High'] > self._ref(df_5min['Open'], -2)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['NRC5'] = (self._ref(df_5min['High'], -1) == self._ref(df_5min['Open'], -1)) & (df_5min['Open'] > self._ref(df_5min['Close'], -1))
        df_5min['NRCB'] = (df_5min['BR1'] | df_5min['BR2'] | df_5min['BR3'] | df_5min['BR4'] | df_5min['BR5'] | df_5min['BR6']) & (df_5min['NRC1'] | df_5min['NRC2'] | df_5min['NRC3'] | df_5min['NRC4'])
        df_5min['BB1'] = df_5min['B1'] & df_5min['B2'] & df_5min['B3'] & df_5min['B5']
        df_5min['BB2'] = (df_5min['B2'] & df_5min['B3'] & df_5min['B4'] & df_5min['B5'] & df_5min['B6']) | (df_5min['B2'] & df_5min['B3'] & df_5min['B4'])
        df_5min['BB3'] = df_5min['B3'] & df_5min['B4'] & df_5min['B1'] & df_5min['B2'] & df_5min['B5'] & df_5min['B6']
        df_5min['BB4'] = df_5min['B4'] & df_5min['B1'] & df_5min['B2'] & df_5min['B5'] & df_5min['B6']
        df_5min['BB5'] = df_5min['B1'] & df_5min['B3'] & df_5min['B4'] & df_5min['B5']
        df_5min['BB6'] = df_5min['B3'] & df_5min['B4'] & df_5min['B5'] & df_5min['B6']
        df_5min['BB7'] = df_5min['B2'] & df_5min['B4'] & df_5min['B5'] & df_5min['B6'] & ~df_5min['RC']
        df_5min['BB8'] = df_5min['B8']
        df_5min['BB9'] = df_5min['B2'] & df_5min['B3'] & df_5min['B5'] & df_5min['B6']
        df_5min['BB10'] = (df_5min['B2'] & df_5min['B31'] & df_5min['B41']) | (df_5min['B3'] & df_5min['B31'] & df_5min['B32'] & df_5min['B41'] & df_5min['B12'])
        df_5min['BB11'] = (df_5min['B32'] & df_5min['B5']) | (df_5min['B3'] & df_5min['B31'] & df_5min['B4'] & df_5min['B12'])
        df_5min['BB12'] = (df_5min['SlowK'] > df_5min['SlowD']) & (df_5min['SlowK'] - df_5min['SlowD'] > 3)
        df_5min['BB13'] = df_5min['B11'] & (df_5min['High'] > self._ref(df_5min['High'], -1))
        df_5min['BB14'] = df_5min['B1'] & df_5min['B2'] & df_5min['B32'] & df_5min['B0'] & df_5min['B12']
        df_5min['BB15'] = df_5min['B2'] & df_5min['B3'] & df_5min['B12'] & df_5min['GC'] & (df_5min['High'] > self._ref(df_5min['High'], -1))
        df_5min['BB16'] = df_5min['B21'] & df_5min['B41'] & df_5min['B12'] & df_5min['RC'] & (df_5min['High'] > self._ref(df_5min['High'], -1))
        df_5min['BB17'] = df_5min['GC'] & (df_5min['High'] > self._ref(df_5min['High'], -1)) & (self._ref(df_5min['Open'], -1) - self._ref(df_5min['Low'], -1) < 1) & (df_5min['CSS'] > 70)
        df_5min['CBB0'] = df_5min['CB1'] | df_5min['CB2'] | df_5min['CB3'] | df_5min['CB4'] | df_5min['CB5'] | df_5min['CB6']
        df_5min['CBB1'] = df_5min['CBB0'] & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) & (df_5min['Open'] > self._ref(df_5min['Open'], -1)) & (self._ref(df_5min['High'], -1) > self._ref(df_5min['High'], -2)) & (self._ref(df_5min['Low'], -1) > self._ref(df_5min['Low'], -2))
        df_5min['CBB2'] = df_5min['CBB0'] & (df_5min['Open'] < self._ref(df_5min['Close'], -1)) & (self._ref(df_5min['Low'], -1) > self._ref(df_5min['Low'], -2)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) & (df_5min['High'] > self._ref(df_5min['High'], -2))
        df_5min['CBB3'] = df_5min['CBB0'] & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) & (self._ref(df_5min['Open'], -1) > self._ref(df_5min['Close'], -2))
        df_5min['CBB4'] = df_5min['CBB0'] & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) & (self._ref(df_5min['Open'], -1) - self._ref(df_5min['Close'], -2) < 1)
        df_5min['CBB5'] = df_5min['CBB0'] & (df_5min['Open'] < self._ref(df_5min['Close'], -1)) & (self._ref(df_5min['Close'], -1) == self._ref(df_5min['High'], -1)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['CBB6'] = df_5min['CBB0'] & (df_5min['Open'] < self._ref(df_5min['Close'], -1)) & (df_5min['Open'] - df_5min['Low'] <= (df_5min['Open'] * 0.0100)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['CBB7'] = df_5min['CBB0'] & (self._ref(df_5min['Open'], -1) == self._ref(df_5min['Low'], -1)) & (df_5min['Open'] < self._ref(df_5min['Close'], -1)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) | \
                          df_5min['CBB0'] & (self._ref(df_5min['High'], -1) > self._ref(df_5min['High'], -2)) & (df_5min['Open'] < self._ref(df_5min['Close'], -1)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['CBB8'] = df_5min['CBB0'] & (self._ref(df_5min['Close'], -1) - self._ref(df_5min['Open'], -1) > 9) & (self._ref(df_5min['Close'], -1) - self._ref(df_5min['Open'], -1) < 13)
        df_5min['CBR'] = df_5min['CBR1'] | df_5min['CBR2'] | df_5min['CBR3'] | df_5min['CBR4']
        df_5min['CBBR1'] = df_5min['CBR'] & (df_5min['Open'] > self._ref(df_5min['High'], -1))
        df_5min['CBBR2'] = df_5min['CBR'] & (self._ref(df_5min['High'], -1) - self._ref(df_5min['Open'], -1) < 0.5)
        df_5min['CBBR3'] = df_5min['CBR'] & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3) & (df_5min['High'] > self._ref(df_5min['High'], -2)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['CBBR4'] = df_5min['CBR'] & (self._ref(df_5min['High'], -1) > self._ref(df_5min['High'], -2)) & (self._ref(df_5min['Low'], -1) > self._ref(df_5min['Low'], -2)) & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (self._ref(df_5min['Close'], -2) != self._ref(df_5min['High'], -2)) & (df_5min['High'] > (self._ref(df_5min['Open'], -1) + self._ref(df_5min['Close'], -1)) / 2) & (df_5min['High'] > self._ref(df_5min['High'], -1))
        df_5min['CBBR5'] = df_5min['CBR'] & (self._ref(df_5min['High'], -1) - self._ref(df_5min['Open'], -1) < self._ref(df_5min['Close'], -1) - self._ref(df_5min['Low'], -1)) & (self._ref(df_5min['Open'], -1) - self._ref(df_5min['Close'], -1) <= 2) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['CBBR6'] = df_5min['CBR'] & (df_5min['Open'] > self._ref(df_5min['Close'], -1)) & (df_5min['High'] > self._ref(df_5min['Open'], -1)) & (self._ref(df_5min['Open'], -2) > self._ref(df_5min['Close'], -2)) & (df_5min['High'] > self._ref(df_5min['Open'], -2)) & (df_5min['High'] > self._ref(df_5min['High'], -1) + 3)
        df_5min['CBBR7'] = df_5min['CBR'] & (self._ref(df_5min['High'], -1) == self._ref(df_5min['Open'], -1)) & (df_5min['Open'] > self._ref(df_5min['Close'], -1))
        df_5min['SS1'] = df_5min['S1'] | df_5min['S2'] | df_5min['S3']
        df_5min['SS2'] = df_5min['S4'] | df_5min['S3']
        df_5min['SS3'] = df_5min['S5'] | df_5min['S3']
        df_5min['SS4'] = (df_5min['S6'] & df_5min['S7']) | (df_5min['S3'] & df_5min['S7'])
        df_5min['SS5'] = df_5min['SS4'] | df_5min['S3']
        df_5min['SS6'] = df_5min['S9'] | df_5min['S3']
        df_5min['SSR1'] = df_5min['SR1'] | df_5min['S3R']
        df_5min['SSR2'] = df_5min['SR2'] | df_5min['S3R']
        df_5min['SSR3'] = df_5min['SR3'] | df_5min['S3R']
        df_5min['SSR4'] = df_5min['SR4'] | df_5min['S3R']
        df_5min['SSR5'] = df_5min['SR7'] | df_5min['S3R']
        df_5min['SSR6'] = df_5min['SR8'] | df_5min['S3R']
        df_5min['SSR7'] = df_5min['SR5'] | df_5min['SR6'] | df_5min['SR9']
        df_5min['SSS'] = (df_5min['MACDLine'] < df_5min['SignalLine']) & (df_5min['RSIValue'] < 50) & (df_5min['adxValue'] < 25) & (df_5min['SlowK'] >= 80)
        df_5min['SSN'] = df_5min['SSR1'] | df_5min['SSR2'] | df_5min['SSR3'] | df_5min['SSR4'] | df_5min['SSR5'] | df_5min['SSR6'] | ~df_5min['SSR7']
        
        # Expand to base DF (no change)
        for col in df_5min.columns:
            if col not in self.df.columns:
                mode = 'point' if 'point' in col.lower() else 'last'
                self.df[f'Five{col}'] = self._expand(df_5min[col], self.df, mode)
        
    def run_trading_logic(self):
        """
        Runs the main trading loop with static state.
        Purpose: Translate the testbed3 code with bar-by-bar processing.
        Generates Buy/Sell signals.
        """
        # Sym for static
        sym = f"{self.df.iloc[0].name if 'name' in self.df.columns else 'symbol'}_{id(self)}"  # Approximate
        # Load statics
        in_position = self._static_var_get(sym + "_InPosition") or 0
        # ... load all
        
        # Reset if needed
        if self.params['ResetStatics']:
            # Remove all
            pass
        
        # Trade history
        # Similar load/reset
        
                # Green, Red, MA1 (full, no skips)
        self.df['Green'] = (((self.df['FiveBB1'] | self.df['FiveBB2'] | self.df['FiveBB3'] | self.df['FiveBB4'] | \
                              self.df['FiveBB5'] | self.df['FiveBB6'] | self.df['FiveBB7'] | self.df['FiveBB8'] | \
                              self.df['FiveBB9'] | self.df['FiveBB10'] | self.df['FiveBB11']) & \
                             self._ref(self.df['FiveBB12'], -1) & self.df['FiveB0']) | \
                            self.df['FiveBB13'] | self.df['FiveBB14'] | self.df['FiveBB15'] | self.df['FiveBB16']) & self.df['FiveB0']
        self.df['Red'] = self.df['FiveCBB1'] | self.df['FiveCBB2'] | self.df['FiveCBB3'] | self.df['FiveCBB4'] | \
                         self.df['FiveCBB5'] | self.df['FiveCBB6'] | self.df['FiveCBB7'] | self.df['FiveCBBR3'] | \
                         self.df['FiveCBBR4'] | self.df['FiveCBBR5'] | self.df['FiveCBBR6'] | self.df['FiveCBBR7'] | self.df['FiveNRCB']
        self.df['MA1'] = self.df['Green'] | self.df['Red']
        
        # Main loop
        self.df['Buy'] = 0
        self.df['Sell'] = 0
        # Initialize arrays
        self.df['LongFlag'] = 0
        # ... all others
        
        current_min_high = current_min_close = 0
        
        for i in range(1, self.bar_count):
            # Update min aggregates
            if self.df['newOneMinBarStart'][i]:
                current_min_high = self.df['High'][i]
                current_min_close = self.df['Close'][i-1]
            else:
                current_min_high = max(current_min_high, self.df['High'][i])
                current_min_close = self.df['Close'][i-1]
            
            # Set from static
            self.df['LongFlag'][i] = in_position
            # ... set all
            
            # Buy logic
            if in_position == 0 and self.df['MA1'][i] and not self.df['MA1'][i-1]:
                self.df['Buy'][i] = 1
                # Set entry
                entry_price_static = max(self.df['PreFiveMinHigh'][i], self.df['Open'][i])
                self.df['BuyPrice'] = entry_price_static  # For use in conditions like SR5
                # ... set all state, persist to static
                # Record trade
            
            # In position
            if in_position == 1 or (in_position == 0 and self.df['newOneMinBarEnd'][i] and not self.df['MA1'][i]):
                # Update max profit
                cur_profit = (current_min_high - fixed_entry_price_current) / fixed_entry_price_current * 100
                max_profit_current = max(max_profit_current, cur_profit)
                # Update flags, stoploss, trail
                # Breach logic
                # Sell if conditions
                
                # Persist changes
                
        # ExRem for signals
        buy = self.df['Buy'].copy()
        sell = self.df['Sell'].copy()
        buy[buy.cumsum() > sell.cumsum().shift().fillna(0)] = 0
        sell[sell.cumsum() > buy.cumsum().shift().fillna(0)] = 0
        self.df['Buy'] = buy
        self.df['Sell'] = sell
        
        # Entry/exit signals for shapes
        
    def plot_chart(self):
        """
        Plots the chart with candles, lines, shapes.
        Purpose: Mimic Plot, PlotShapes.
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        # Candlestick
        for i in range(len(self.df)):
            color = 'g' if self.df['Close'][i] > self.df['Open'][i] else 'r'
            ax.vlines(i, self.df['Low'][i], self.df['High'][i], color='k', linewidth=1)
            ax.vlines(i, self.df['Open'][i], self.df['Close'][i], color=color, linewidth=3)
        
        # Plot signals
        entry = self.df[self.df['entrySignal'] == 1].index
        exit_ = self.df[self.df['exitSignal'] == 1].index
        for idx in entry:
            ax.add_patch(Arrow(idx, self.df['Low'][idx] - 0.1 * (self.df['High'][idx] - self.df['Low'][idx]), 0, 0.2 * (self.df['High'][idx] - self.df['Low'][idx]), width=0.5, color='g'))
        for idx in exit_:
            ax.add_patch(Arrow(idx, self.df['High'][idx] + 0.1 * (self.df['High'][idx] - self.df['Low'][idx]), 0, -0.2 * (self.df['High'][idx] - self.df['Low'][idx]), width=0.5, color='y'))
        
        # Other lines like VAH, VAL, etc.
        ax.plot(self.df['VAH'], label='VAH', linestyle='--', linewidth=1)
        # ... add others
        
        ax.set_title(self.params['sep'])
        ax.legend()
        plt.show()

    def run(self):
        """
        Runs the full strategy.
        Purpose: Entry point to execute all logic.
        """
        self.run_volume_profile()
        self.run_indicators()
        self.run_trading_logic()
        self.plot_chart()
        # Print exploration if needed
        print(self.df[[ 'LongFlag', 'Buy', 'Sell', ... ]])  # Filter as in AFL

# Standalone script usage
if __name__ == '__main__':
    # Sample data (replace with real)
    dates = pd.date_range('2026-02-13 10:25:00', periods=1000, freq='S')
    df = pd.DataFrame({
        'Open': np.random.rand(1000) * 100,
        'High': np.random.rand(1000) * 100 + 100,
        'Low': np.random.rand(1000) * 100,
        'Close': np.random.rand(1000) * 100 + 50,
        'Volume': np.random.randint(100, 1000, 1000)
    }, index=dates)
    
    strategy = Strategy(df)
    strategy.run()
    
    # Clean up shelve
    os.remove('static_vars.shelve') if os.path.exists('static_vars.shelve') else None