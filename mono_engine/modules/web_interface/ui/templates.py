"""
UI Templates for the web interface.
Provides HTML templates and frontend assets.
"""


def get_main_template(data=None):
    """
    Get the main HTML template for the dashboard.

    Args:
        data: Optional data dictionary with signals and trades

    Returns:
        HTML template string
    """
    if data is None:
        data = {'signals': [], 'trades': []}

    signals = data.get('signals', [])
    trades = data.get('trades', [])

    # Calculate stats
    total_signals = len(signals)
    active_trades = len([t for t in trades if not t.get('exit_time')])
    completed_trades = [t for t in trades if t.get('exit_time') and t.get('realized_pnl') is not None]
    total_pnl = sum(t.get('realized_pnl', 0) for t in completed_trades)
    winning_trades = len([t for t in completed_trades if t.get('realized_pnl', 0) > 0])
    win_rate = (winning_trades / len(completed_trades) * 100) if completed_trades else 0

    # Stats for template
    pnl_class = 'positive' if total_pnl >= 0 else 'negative'
    total_pnl_abs = abs(total_pnl)
    win_class = 'positive' if win_rate >= 50 else 'negative'

    # Generate HTML for signals table
    signals_html = ""
    if signals:
        for signal in signals[:10]:  # Show first 10
            signal_time = signal.get('signal_time', '')
            symbol = signal.get('symbol', '')
            signal_type = signal.get('signal_type', '')
            signal_reason = signal.get('signal_reason', '')
            signal_price = "{:.2f}".format(signal.get('signal_price', 0)) if signal.get('signal_price') else '-'
            candle_close = "{:.2f}".format(signal.get('candle_close', 0)) if signal.get('candle_close') else '-'
            status = signal.get('status', '')
            is_live = '🔴 LIVE' if signal.get('is_live') else '📊 HISTORICAL'

            signals_html += """<tr><td>{}</td><td>{}</td><td><span class="status-badge signal-type-{}">{}</span></td><td>{}</td><td>{}</td><td>{}</td><td><span class="status-badge status-{}">{}</span></td><td>{}</td></tr>""".format(
                signal_time, symbol, signal_type, signal_type.upper(), signal_reason, signal_price, candle_close, status, status, is_live
            )
    else:
        signals_html = '<tr><td colspan="8" class="no-data">No signals found</td></tr>'

    # Generate HTML for trades table
    trades_html = ""
    if trades:
        for trade in trades[:10]:  # Show first 10
            realized_pnl = trade.get('realized_pnl')
            pnl_value = realized_pnl if realized_pnl is not None else 0
            pnl_class = 'positive' if pnl_value > 0 else ('negative' if pnl_value < 0 else 'neutral')
            pnl_text = "₹{:,.0f}".format(abs(pnl_value)) if realized_pnl is not None else '-'
            pnl_percent = "{:.2f}%".format(((trade.get('exit_price', 0) - trade.get('entry_price', 0)) / trade.get('entry_price', 0) * 100)) if trade.get('exit_price') and trade.get('entry_price') else '-'
            close_price = "{:.2f}".format(trade.get('exit_price', 0)) if trade.get('exit_price') else '-'

            entry_time = trade.get('entry_time', '')
            symbol = trade.get('symbol', '')
            buy_reason = trade.get('buy_reason', '')
            sell_reason = trade.get('sell_reason', '') or '-'
            entry_price = "{:.2f}".format(trade.get('entry_price', 0))
            exit_price = "{:.2f}".format(trade.get('exit_price', 0)) if trade.get('exit_price') else '-'

            trades_html += """<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>900</td><td class="{}">{}</td><td class="{}">{}</td></tr>""".format(
                entry_time, symbol, buy_reason, sell_reason, entry_price, exit_price, close_price, pnl_class, pnl_text, pnl_class, pnl_percent
            )
    else:
        trades_html = '<tr><td colspan="10" class="no-data">No trades found</td></tr>'

    # Simple server-side rendered HTML - NO JAVASCRIPT!
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MoNo Engine - Trading Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}

        .header p {{
            color: #666;
            font-size: 1.1rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
        }}

        .stat-card h3 {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            font-size: 0.85rem;
            color: #888;
        }}

        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .neutral {{ color: #6b7280; }}

        .tabs {{
            display: flex;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 5px;
            margin-bottom: 30px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }}

        .tab {{
            flex: 1;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 500;
        }}

        .tab.active {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}

        .tab-content {{
            display: none;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .tab-content.active {{ display: block; }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9rem;
        }}

        .data-table th,
        .data-table td {{
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}

        .data-table th {{
            background: #f8fafc;
            font-weight: 600;
            color: #374151;
            position: sticky;
            top: 0;
        }}

        .data-table tr:hover {{
            background: #f8fafc;
        }}

        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }}

        .status-signaled {{ background: #fef3c7; color: #d97706; }}
        .status-filled {{ background: #dbeafe; color: #2563eb; }}
        .status-completed {{ background: #d1fae5; color: #065f46; }}

        .signal-type-buy {{ background: #dbeafe; color: #1e40af; }}
        .signal-type-sell {{ background: #fee2e2; color: #dc2626; }}

        .no-data {{
            text-align: center;
            padding: 50px;
            color: #6b7280;
            font-style: italic;
        }}

        @media (max-width: 768px) {{
            .dashboard {{ padding: 10px; }}
            .header {{ padding: 20px; }}
            .header h1 {{ font-size: 2rem; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 MoNo Engine Dashboard</h1>
            <p>Real-time trading signals and performance analytics</p>
            <div style="margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 8px; font-size: 14px; color: #333;">Data loaded successfully! {} signals and {} trades.</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Signals</h3>
                <div class="value">{}</div>
                <div class="label">All time</div>
            </div>
            <div class="stat-card">
                <h3>Active Trades</h3>
                <div class="value">{}</div>
                <div class="label">Currently open</div>
            </div>
            <div class="stat-card">
                <h3>Total PnL</h3>
                <div class="value"><span class="{}">₹{:,.0f}</span></div>
                <div class="label">Realized profit/loss</div>
            </div>
            <div class="stat-card">
                <h3>Win Rate</h3>
                <div class="value"><span class="{}">{:.1f}%</span></div>
                <div class="label">Successful trades</div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active">📡 Signals</div>
            <div class="tab">📊 All Trades</div>
        </div>

        <div class="tab-content active">
            <h3 style="margin-bottom: 20px; color: #374151;">Recent Signals</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Symbol</th>
                        <th>Type</th>
                        <th>Reason</th>
                        <th>Price</th>
                        <th>Close</th>
                        <th>Status</th>
                        <th>Live</th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
        </div>

        <div class="tab-content">
            <h3 style="margin-bottom: 20px; color: #374151;">Recent Trades</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Entry Time</th>
                        <th>Symbol</th>
                        <th>Buy Reason</th>
                        <th>Sell Reason</th>
                        <th>Entry Price</th>
                        <th>Exit Price</th>
                        <th>Close</th>
                        <th>Quantity</th>
                        <th>PnL Amount</th>
                        <th>PnL %</th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Simple tab switching - minimal JavaScript
        document.addEventListener('DOMContentLoaded', function() {{
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');

            tabs.forEach((tab, index) => {{
                tab.addEventListener('click', function() {{
                    tabs.forEach(t => t.classList.remove('active'));
                    contents.forEach(c => c.classList.remove('active'));

                    tab.classList.add('active');
                    contents[index].classList.add('active');
                }});
            }});
        }});
    </script>
</body>
</html>""".format(
        total_signals, len(trades),
        total_signals, active_trades,
        pnl_class, total_pnl_abs,
        win_class, win_rate,
        signals_html, trades_html
    )

    return html_content
