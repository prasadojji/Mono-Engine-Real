# tests/test_dummy_strategy.py
"""
Dummy MACD/RSI Strategy for testing workflow
- Buy: MACD line crosses above signal on 5min timeframe
- Sell: RSI(14) < 30 on latest 1min bar
- Long-only flavor (simple internal flag to avoid repeat buys)
"""
import sys
import os
import numpy as np

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
import pandas as pd
import talib
from mono_engine.strategies.base_strategy import BaseStrategy


class DummyMacdRsiStrategy(BaseStrategy):
    """
    Minimal dummy strategy to test candle delivery and signal generation.
    Uses only MACD on 5min and RSI on 1min — easy to trigger for testing.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        
        # Fixed simple parameters
        self.macd_fast = 5
        self.macd_slow = 10
        self.macd_signal = 4
        self.rsi_period = 14
        
        # Accumulation
        self.df_1min = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        self.df_5min = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Simple state (for testing only — real state comes from engine)
        self.in_trade = False
        
        print("[DummyStrategy] Initialized with MACD(12,26,9) and RSI(14)")

    def on_data_update(self, data: dict[str, pd.DataFrame]):
        if '1min' in data and not data['1min'].empty:
            new_1min = data['1min']
            # Cast only existing numeric columns
            numeric_cols = [col for col in ['Open', 'High', 'Low', 'Close', 'Volume'] if col in new_1min.columns]
            if numeric_cols:
                new_1min = new_1min.astype({col: float for col in numeric_cols})
            print(f"[Dummy] Received {len(new_1min)} new 1min bars")
            self.df_1min = pd.concat([self.df_1min, new_1min]).drop_duplicates(keep='last')
            print(f"  → Total 1min bars now: {len(self.df_1min)}")

        if '5min' in data and not data['5min'].empty:
            new_5min = data['5min']
            numeric_cols = [col for col in ['Open', 'High', 'Low', 'Close', 'Volume'] if col in new_5min.columns]
            if numeric_cols:
                new_5min = new_5min.astype({col: float for col in numeric_cols})
            print(f"[Dummy] Received {len(new_5min)} new 5min bars")
            self.df_5min = pd.concat([self.df_5min, new_5min]).drop_duplicates(keep='last')
            print(f"  → Total 5min bars now: {len(self.df_5min)}")
    
    def should_enter(self) -> tuple[bool, float | None]:
        """
        Buy condition: MACD line crosses above signal on latest 5min bar.
        Returns (True, suggested price) or (False, None)
        """
        if self.df_5min.empty or len(self.df_5min) < 2:
            print("[Dummy] Not enough 5min data for MACD")
            return False, None

        close = self.df_5min['Close'].astype(float).values  # Force float
        macd, signal, _ = talib.MACD(
            close.astype(np.float64),  # Explicit cast
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal
        )

        if len(macd) < 2:
            print("[Dummy] MACD calculation needs more bars")
            return False, None

        current_macd = macd[-1]
        current_signal = signal[-1]
        prev_macd = macd[-2]
        prev_signal = signal[-2]

        print(f"[Debug MACD] Last bar: MACD={current_macd:.4f}, Signal={current_signal:.4f}")
        print(f"[Debug MACD] Prev bar: MACD={prev_macd:.4f}, Signal={prev_signal:.4f}")

        crossover_up = (current_macd > current_signal) and (prev_macd <= prev_signal or current_macd - current_signal > 0.5)  # add momentum check

        if crossover_up and not self.in_trade:
            price = self.df_5min['Close'].iloc[-1]
            print(f"[Dummy] BUY SIGNAL: MACD crossover on 5min at {price}")
            self.in_trade = True  # Simple flag for demo
            return True, price

        return False, None

    def should_exit(self) -> tuple[bool, float | None]:
        """
        Sell condition: RSI < 30 on latest 1min bar.
        Returns (True, suggested price) or (False, None)
        """
        if self.df_1min.empty or len(self.df_1min) < self.rsi_period:
            print("[Dummy] Not enough 1min data for RSI")
            return False, None

        close = self.df_1min['Close'].astype(float).values
        rsi = talib.RSI(close.astype(np.float64), timeperiod=self.rsi_period)

        if len(rsi) == 0:
            return False, None

        latest_rsi = rsi[-1]
        if latest_rsi < 30:
            price = self.df_1min['Close'].iloc[-1]
            print(f"[Dummy] SELL SIGNAL: RSI oversold ({latest_rsi:.2f}) on 1min at {price}")
            self.in_trade = False  # Reset flag
            return True, price

        return False, None

    def reset_day(self):
        """Optional reset at new day"""
        self.df_1min = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        self.df_5min = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        self.in_trade = False
        print("[Dummy] Reset for new day")


if __name__ == "__main__":
    print("Running quick standalone test for DummyMacdRsiStrategy...")
    dummy = DummyMacdRsiStrategy()
    
    # === Fake 5min data — acceleration starts early and builds strongly ===
    dates_5min = pd.date_range("2026-02-18 09:00", periods=40, freq='5min')
    
    # 40 bars: gentle first 10 → acceleration from bar 11 onward
    close_5min = [100.0] * 10  # flat start
    current = 100.0
    for i in range(30):
        increment = 0.5 + i * 0.4  # starts small, grows to large steps
        current += increment
        close_5min.append(current)
    
    fake_5min = pd.DataFrame({
        'Open':  [c - 0.8 for c in close_5min],
        'High':  [c + 1.5 for c in close_5min],
        'Low':   [c - 1.5 for c in close_5min],
        'Close': close_5min,
        'Volume': [1000 + i*80 for i in range(40)]
    }, index=dates_5min)
    
    print("\nFeeding 5min uptrend data in small batches (simulate live arrival)...")
    batch_size = 5
    buy_triggered = False
    for start in range(0, len(fake_5min), batch_size):
        batch = fake_5min.iloc[start:start + batch_size]
        print(f"  Batch {start // batch_size + 1} ({len(batch)} bars)")
        dummy.on_data_update({'5min': batch})
        
        enter, price = dummy.should_enter()
        if enter:
            print(f"TEST BUY triggered at {price:.2f} (MACD crossover in this batch)")
            buy_triggered = True

    if not buy_triggered:
        # Final debug (fixed - no self)
        if len(dummy.df_5min) >= 2:
            close = dummy.df_5min['Close'].values
            macd, signal, _ = talib.MACD(close, 12, 26, 9)  # Use same periods as class
            if len(macd) >= 2:
                print(f"[Final Debug MACD] Last: MACD={macd[-1]:.4f}, Signal={signal[-1]:.4f}")
                print(f"[Final Debug MACD] Prev: MACD={macd[-2]:.4f}, Signal={signal[-2]:.4f}")
        print("No BUY trigger across all batches — MACD never crossed in a single batch")

    # === 1min data (unchanged — already good) ===
    dates_1min = pd.date_range("2026-02-18 09:00", periods=40, freq='1min')
    close_1min = (
        [100.0 + i*0.05 for i in range(25)] +   # gentle rise
        [98, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30]  # sharp drop
    )
    fake_1min = pd.DataFrame({
        'Open':  close_1min,
        'High':  [c + 0.3 for c in close_1min],
        'Low':   [c - 0.3 for c in close_1min],
        'Close': close_1min,
        'Volume': [800 + i*10 for i in range(40)]
    }, index=dates_1min)
    
    print("\nFeeding 1min oversold drop data (40 bars)...")
    dummy.on_data_update({'1min': fake_1min})
    
    exit_, price = dummy.should_exit()
    if exit_:
        print(f"TEST SELL triggered at {price:.2f} (RSI < 30)")
    else:
        print("No SELL trigger — RSI may not be <30 yet")

    print("\nStandalone test complete. Check prints for signals.")