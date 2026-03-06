"""
Multi-Symbol Historical Backtest with Caching
- Runs all symbols from historical_symbols.json in parallel
- Caches results by strategy_version + symbol
- Web interface for results visualization and filtering
"""

import logging
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from tabulate import tabulate
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseModule


class HistoricalBacktest(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)

        # Dual versioning system
        strategy_versions = self.engine.config.get('strategy_versions', {})
        self.buy_version = strategy_versions.get('buy_version', 'Buy_AFL_v1.0')
        self.sell_version = strategy_versions.get('sell_version', 'Stoploss_v2.1')

        # Get quantity from config (stoploss_params or other section)
        stoploss_params = self.engine.config.get('stoploss_params', {})
        self.default_quantity = stoploss_params.get('quantity', 900)  # Default to 900 if not set

        self.db_path = 'mono_engine_data.db'
        self.historical_file = 'historical_symbols.json'
        self.max_workers = min(8, os.cpu_count() or 4)  # Parallel processing

    def start(self):
        self.run()

    def stop(self):
        pass

    def run(self):
        self.logger.info("=" * 100)
        self.logger.info("🚀 MULTI-SYMBOL HISTORICAL BACKTEST WITH DUAL VERSIONING")
        self.logger.info(f"Buy Version: {self.buy_version} | Sell Version: {self.sell_version}")
        self.logger.info("Parallel processing + intelligent caching")
        self.logger.info("=" * 100)

        # Load symbols from historical_symbols.json
        symbols = self._load_symbols()
        if not symbols:
            self.logger.error("No symbols found in historical_symbols.json")
            return

        self.logger.info(f"Loaded {len(symbols)} symbols for backtesting")

        # Check cache and run backtests
        cached_results = {}
        symbols_to_run = []

        for symbol_info in symbols:
            symbol = symbol_info['symbol']
            cache_key = (symbol, self.buy_version, self.sell_version)

            if self._is_cached(cache_key):
                self.logger.info(f"📋 {symbol}: Loading from cache")
                cached_results[symbol] = self._load_cached_results(cache_key)
            else:
                self.logger.info(f"🔄 {symbol}: Will run fresh backtest")
                symbols_to_run.append(symbol_info)

        # Run fresh backtests in parallel
        if symbols_to_run:
            self.logger.info(f"Running {len(symbols_to_run)} fresh backtests in parallel...")
            fresh_results = self._run_parallel_backtests(symbols_to_run)

            # Save to cache
            for symbol, result in fresh_results.items():
                cache_key = (symbol, self.buy_version, self.sell_version)
                self._save_to_cache(cache_key, result)
                cached_results[symbol] = result

        # Aggregate and display results
        self._display_aggregate_results(cached_results)

        # Launch web interface
        self._launch_web_interface()

    def _load_symbols(self):
        """Load symbols from historical_symbols.json, excluding index symbols"""
        if not os.path.exists(self.historical_file):
            self.logger.error(f"{self.historical_file} not found")
            return []

        try:
            with open(self.historical_file, 'r') as f:
                all_symbols = json.load(f)

            # Filter out index symbols containing -51
            filtered_symbols = []
            skipped_indices = []

            for symbol_info in all_symbols:
                symbol_id = symbol_info.get('id', '')
                if '-51' in symbol_id:
                    skipped_indices.append(symbol_info.get('symbol', symbol_id))
                else:
                    filtered_symbols.append(symbol_info)

            if skipped_indices:
                self.logger.info(f"Skipped {len(skipped_indices)} index symbols: {', '.join(skipped_indices)}")

            self.logger.info(f"Loaded {len(filtered_symbols)} tradable symbols (excluded {len(skipped_indices)} indices)")
            return filtered_symbols

        except Exception as e:
            self.logger.error(f"Failed to load symbols: {e}")
            return []

    def _is_cached(self, cache_key):
        """Check if results exist in cache"""
        symbol, buy_version, sell_version = cache_key
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM backtest_results
            WHERE symbol = ? AND buy_version = ? AND sell_version = ?
        """, (symbol, buy_version, sell_version))

        result = cursor.fetchone()
        conn.close()
        return result is not None

    def _load_cached_results(self, cache_key):
        """Load cached results from database"""
        symbol, buy_version, sell_version = cache_key
        conn = sqlite3.connect(self.db_path)

        # Load summary
        summary_df = pd.read_sql("""
            SELECT * FROM backtest_results
            WHERE symbol = ? AND buy_version = ? AND sell_version = ?
        """, conn, params=(symbol, buy_version, sell_version))

        # Load trades
        trades_df = pd.read_sql("""
            SELECT * FROM backtest_trades
            WHERE symbol = ? AND buy_version = ? AND sell_version = ?
            ORDER BY entry_time
        """, conn, params=(symbol, buy_version, sell_version))

        conn.close()

        if summary_df.empty:
            return None

        summary = summary_df.iloc[0].to_dict()
        trades = trades_df.to_dict('records') if not trades_df.empty else []

        return {
            'summary': summary,
            'trades': trades
        }

    def _run_parallel_backtests(self, symbols_to_run):
        """Run backtests in parallel"""
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._run_single_backtest, symbol_info): symbol_info['symbol']
                for symbol_info in symbols_to_run
            }

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    results[symbol] = result
                    self.logger.info(f"✅ {symbol}: Backtest completed")
                except Exception as e:
                    self.logger.error(f"❌ {symbol}: Backtest failed - {e}")
                    results[symbol] = None

        return results

    def _run_single_backtest(self, symbol_info):
        """Run backtest for a single symbol"""
        symbol = symbol_info['symbol']
        symbol_id = symbol_info.get('id', symbol)

        # Load historical data
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql(f"""
            SELECT timestamp as ts, open, high, low, close, volume
            FROM historical_1min
            WHERE symbol = ?
            ORDER BY timestamp
        """, conn, params=(symbol_id,), parse_dates=['ts'], index_col='ts')
        conn.close()

        if df.empty:
            self.logger.warning(f"No data found for {symbol}")
            return None

        df = df.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume'
        })

        # Initialize strategy and state for this symbol
        strategy_module = self.engine.modules.get('strategy')
        state_module = self.engine.modules.get('state')

        # Set PnL module to historical mode for signal publishing
        pnl_module = self.engine.modules.get('pnl')
        if pnl_module:
            pnl_module.is_historical_run = True

        # Reset strategy and state
        if hasattr(strategy_module, '_get_or_create_strategy'):
            strategy = strategy_module._get_or_create_strategy(symbol)
            if hasattr(strategy, 'reset_day'):
                strategy.reset_day()

        if hasattr(state_module, 'states') and symbol in state_module.states:
            state_module.states[symbol].update(in_trade=False)

        trades = []
        current_buy_reason = "unknown"

        # Event handlers for this symbol
        def on_buy_signal(data):
            nonlocal current_buy_reason
            if data.get('symbol') != symbol:
                return
            price = data.get('price')
            current_buy_reason = data.get('buy_reason', 'unknown')

            fill_data = {
                'order_id': f"HIS-B-{symbol}-{int(datetime.now().timestamp())}",
                'scrip': symbol,
                'order_type': 'buy',
                'price': price,
                'quantity': self.default_quantity,
                'fill_time': datetime.now(),
                'buy_reason': current_buy_reason
            }
            self.engine.events.publish('order_filled', fill_data)

        def on_exit_signal(data):
            nonlocal trades, current_buy_reason
            if data.get('symbol') != symbol:
                return

            exit_price = data.get('exit_price')
            reason = data.get('reason', 'unknown')

            entry = state_module.get_entry_details(symbol)
            if entry:
                pnl_amount = (exit_price - entry.price) * self.default_quantity  # Use configurable quantity
                pnl_percent = (exit_price - entry.price) / entry.price * 100

                trade = {
                    'entry_time': entry.time.strftime('%Y-%m-%d %H:%M:%S'),
                    'exit_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'entry_price': entry.price,
                    'exit_price': exit_price,
                    'quantity': self.default_quantity,
                    'pnl_amount': pnl_amount,
                    'pnl_percent': pnl_percent,
                    'buy_reason': current_buy_reason,
                    'sell_reason': reason
                }
                trades.append(trade)

            fill_data = {
                'order_id': f"HIS-S-{symbol}-{int(datetime.now().timestamp())}",
                'scrip': symbol,
                'order_type': 'sell',
                'price': exit_price,
                'quantity': self.default_quantity,
                'fill_time': datetime.now(),
                'sell_reason': reason
            }
            self.engine.events.publish('order_filled', fill_data)

        # Subscribe to events
        self.events.subscribe('buy_signal', on_buy_signal)
        self.events.subscribe('exit_signal', on_exit_signal)

        # Run backtest
        strategy = strategy_module._get_or_create_strategy(symbol)

        for i, (ts, row) in enumerate(df.iterrows()):
            # Feed data to strategy
            strategy.on_data_update({'1min': df.loc[:ts].tail(100)})

            # Check for entry signal
            if hasattr(strategy, 'should_enter'):
                enter, price, reason = strategy.should_enter()
                if enter:
                    self.engine.events.publish('buy_signal', {
                        'price': price or 0.0,
                        'symbol': symbol,
                        'quantity': self.default_quantity,
                        'buy_reason': reason
                    })

            # Publish bar closed event
            bar_data = {
                'symbol': symbol,
                'bar': {
                    'ts': ts,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
            }
            self.engine.events.publish('1min_bar_closed', bar_data)

            # Force exit after 500 bars if still in trade
            if i == 500 and state_module.is_in_trade(symbol):
                entry = state_module.get_entry_details(symbol)
                if entry:
                    self.engine.events.publish('exit_signal', {
                        'symbol': symbol,
                        'exit_price': row['Close'],
                        'reason': 'FORCED_AFTER_500_BARS'
                    })

        # Unsubscribe
        self.events.unsubscribe('buy_signal', on_buy_signal)
        self.events.unsubscribe('exit_signal', on_exit_signal)

        # Calculate summary statistics
        if trades:
            winning_trades = [t for t in trades if t['pnl_percent'] > 0]
            losing_trades = [t for t in trades if t['pnl_percent'] <= 0]

            total_pnl = sum(t['pnl_amount'] for t in trades)
            avg_trade_pnl = total_pnl / len(trades)
            win_rate = len(winning_trades) / len(trades) * 100

            # Calculate max drawdown (simplified)
            cumulative_pnl = 0
            peak = 0
            max_drawdown = 0
            for trade in trades:
                cumulative_pnl += trade['pnl_amount']
                peak = max(peak, cumulative_pnl)
                drawdown = peak - cumulative_pnl
                max_drawdown = max(max_drawdown, drawdown)

            # Buy/sell reason counts
            buy_reasons = defaultdict(int)
            sell_reasons = defaultdict(int)
            for trade in trades:
                buy_reasons[trade['buy_reason']] += 1
                sell_reasons[trade['sell_reason']] += 1

            summary = {
                'symbol': symbol,
                'buy_version': self.buy_version,
                'sell_version': self.sell_version,
                'total_trades': len(trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_trade_pnl': avg_trade_pnl,
                'max_drawdown': max_drawdown,
                'buy_reasons': json.dumps(dict(buy_reasons)),
                'sell_reasons': json.dumps(dict(sell_reasons))
            }
        else:
            summary = {
                'symbol': symbol,
                'buy_version': self.buy_version,
                'sell_version': self.sell_version,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_trade_pnl': 0.0,
                'max_drawdown': 0.0,
                'buy_reasons': '{}',
                'sell_reasons': '{}'
            }

        return {
            'summary': summary,
            'trades': trades
        }

    def _save_to_cache(self, cache_key, result):
        """Save results to database cache"""
        if not result:
            return

        symbol, buy_version, sell_version = cache_key
        summary = result['summary']
        trades = result['trades']

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Save summary
        cursor.execute("""
            INSERT OR REPLACE INTO backtest_results
            (symbol, buy_version, sell_version, total_trades, winning_trades, losing_trades,
             win_rate, total_pnl, avg_trade_pnl, max_drawdown, buy_reasons, sell_reasons)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            summary['symbol'], summary['buy_version'], summary['sell_version'], summary['total_trades'],
            summary['winning_trades'], summary['losing_trades'], summary['win_rate'],
            summary['total_pnl'], summary['avg_trade_pnl'], summary['max_drawdown'],
            summary['buy_reasons'], summary['sell_reasons']
        ))

        # Save trades
        for trade in trades:
            cursor.execute("""
                INSERT INTO backtest_trades
                (symbol, buy_version, sell_version, entry_time, exit_time, entry_price, exit_price,
                 quantity, pnl_amount, pnl_percent, buy_reason, sell_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol, buy_version, sell_version, trade['entry_time'], trade['exit_time'],
                trade['entry_price'], trade['exit_price'], trade['quantity'],
                trade['pnl_amount'], trade['pnl_percent'], trade['buy_reason'], trade['sell_reason']
            ))

        conn.commit()
        conn.close()

    def _display_aggregate_results(self, results):
        """Display aggregate results across all symbols"""
        self.logger.info("=" * 100)
        self.logger.info("📊 AGGREGATE BACKTEST RESULTS")
        self.logger.info("=" * 100)

        total_trades = 0
        total_winning = 0
        total_pnl = 0.0
        symbol_summaries = []

        for symbol, result in results.items():
            if result and result['summary']['total_trades'] > 0:
                summary = result['summary']
                total_trades += summary['total_trades']
                total_winning += summary['winning_trades']
                total_pnl += summary['total_pnl']

                symbol_summaries.append({
                    'Symbol': symbol,
                    'Trades': summary['total_trades'],
                    'Win Rate': f"{summary['win_rate']:.1f}%",
                    'Total PnL': f"₹{summary['total_pnl']:,.0f}",
                    'Avg Trade': f"₹{summary['avg_trade_pnl']:,.0f}"
                })

        if symbol_summaries:
            print("\nPer-Symbol Summary:")
            print(tabulate(symbol_summaries, headers="keys", tablefmt="grid"))

            overall_win_rate = (total_winning / total_trades * 100) if total_trades > 0 else 0

            print(f"\n{'='*80}")
            print(f"OVERALL RESULTS:")
            print(f"Total Symbols: {len([r for r in results.values() if r])}")
            print(f"Total Trades: {total_trades}")
            print(f"Overall Win Rate: {overall_win_rate:.1f}%")
            print(f"Total PnL: ₹{total_pnl:,.0f}")
            print(f"{'='*80}")
        else:
            print("No trades recorded across any symbols")

    def _launch_web_interface(self):
        """Launch web interface for results visualization"""
        try:
            from .web_interface import app
            import webbrowser
            import threading

            def open_browser():
                webbrowser.open('http://localhost:5000/backtest-results')

            # Start web server in background
            threading.Thread(target=lambda: app.run(debug=False, port=5000), daemon=True).start()

            # Open browser after a short delay
            threading.Timer(2.0, open_browser).start()

            self.logger.info("🌐 Web interface launched at http://localhost:5000/backtest-results")

        except ImportError:
            self.logger.warning("Flask not installed - web interface not available")
            self.logger.info("Install Flask with: pip install flask")
