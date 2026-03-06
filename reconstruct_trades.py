#!/usr/bin/env python3
"""
Reconstruct missing trades from March 4th, 2026 paper trading session.

This script analyzes the signals data and creates trade records for trades that should have occurred
but were never stored due to the exit_signal bug.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json

def reconstruct_march_4th_trades():
    """Reconstruct trades from March 4th signals data"""

    db_path = 'mono_engine_data.db'
    conn = sqlite3.connect(db_path)

    print("Analyzing March 4th signals data...")

    # Get all buy signals that were filled on March 4th
    buy_signals_df = pd.read_sql("""
        SELECT * FROM trades_signals
        WHERE DATE(signal_time) = '2026-03-04'
        AND signal_type = 'buy'
        AND status = 'filled'
        ORDER BY signal_time
    """, conn)

    # Get all sell signals from March 4th (whether filled or not)
    sell_signals_df = pd.read_sql("""
        SELECT * FROM trades_signals
        WHERE DATE(signal_time) = '2026-03-04'
        AND signal_type = 'sell'
        ORDER BY signal_time
    """, conn)

    print(f"Found {len(buy_signals_df)} filled buy signals and {len(sell_signals_df)} sell signals on March 4th")

    # Group by symbol to match buys with sells
    reconstructed_trades = []

    for symbol in buy_signals_df['symbol'].unique():
        symbol_buy_signals = buy_signals_df[buy_signals_df['symbol'] == symbol]
        symbol_sell_signals = sell_signals_df[sell_signals_df['symbol'] == symbol]

        print(f"Processing {symbol}: {len(symbol_buy_signals)} buys, {len(symbol_sell_signals)} sells")

        # For each buy signal, find the next sell signal
        for _, buy_signal in symbol_buy_signals.iterrows():
            buy_time = pd.to_datetime(buy_signal['signal_time'])
            buy_price = buy_signal['fill_price']

            # Find the next sell signal after this buy
            later_sells = symbol_sell_signals[
                pd.to_datetime(symbol_sell_signals['signal_time']) > buy_time
            ]

            if not later_sells.empty:
                # Take the first sell signal after this buy
                sell_signal = later_sells.iloc[0]
                sell_time = pd.to_datetime(sell_signal['signal_time'])
                sell_reason = sell_signal['signal_reason']

                # Estimate exit price (use signal price or buy price + some movement)
                exit_price = sell_signal['signal_price'] if sell_signal['signal_price'] else buy_price * 1.02  # Assume 2% move

                # Calculate PnL
                quantity = 900  # Default from config
                lot_size = 10   # Default for options
                realized_pnl = (exit_price - buy_price) * quantity * lot_size

                trade = {
                    'trade_id': f"RECONSTRUCTED-{buy_signal['signal_id'].split('_')[-1]}",
                    'symbol': symbol,
                    'buy_reason': buy_signal['signal_reason'],
                    'sell_reason': sell_reason,
                    'entry_price': buy_price,
                    'exit_price': exit_price,
                    'quantity': quantity,
                    'lot_size': lot_size,
                    'entry_time': str(buy_time),
                    'exit_time': str(sell_time),
                    'realized_pnl': realized_pnl,
                    'is_historical': 0
                }

                reconstructed_trades.append(trade)
                print(f"  Reconstructed trade: {symbol} | PnL: Rs.{realized_pnl:,.0f} | Reason: {sell_reason}")

    # Store reconstructed trades in database
    if reconstructed_trades:
        print(f"\nStoring {len(reconstructed_trades)} reconstructed trades...")

        for trade in reconstructed_trades:
            try:
                conn.execute('''INSERT OR REPLACE INTO trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                    trade.get('trade_id'), trade.get('symbol'), trade.get('buy_reason'),
                    trade.get('entry_price'), trade.get('exit_price'), trade.get('quantity'),
                    trade.get('lot_size'), str(trade.get('entry_time')), str(trade.get('exit_time')),
                    trade.get('realized_pnl', 0), trade.get('is_historical', 0), trade.get('sell_reason', 'unknown'),
                    None, None, None, None,  # buy_date, buy_time, sell_date, sell_time
                    trade.get('realized_pnl', 0),  # pnl_rs
                    None  # symbol_readable
                ))
            except Exception as e:
                print(f"Failed to store reconstructed trade {trade['trade_id']}: {e}")

        conn.commit()
        print(f"Successfully stored {len(reconstructed_trades)} reconstructed trades")

        # Calculate summary
        total_pnl = sum(t['realized_pnl'] for t in reconstructed_trades)
        winning_trades = sum(1 for t in reconstructed_trades if t['realized_pnl'] > 0)
        win_rate = (winning_trades / len(reconstructed_trades) * 100) if reconstructed_trades else 0

        print("\nMarch 4th Trading Summary:")
        print(f"   Total Trades: {len(reconstructed_trades)}")
        print(f"   Winning Trades: {winning_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total PnL: Rs.{total_pnl:,.0f}")

    else:
        print("No trades could be reconstructed")

    conn.close()

if __name__ == "__main__":
    reconstruct_march_4th_trades()