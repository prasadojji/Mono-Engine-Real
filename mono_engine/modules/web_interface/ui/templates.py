"""
UI Templates for the web interface.
Provides HTML templates and frontend assets.
"""


def get_main_template():
    """
    Get the main HTML template for the dashboard.

    Returns:
        HTML template string
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MoNo Engine - Trading Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
        }

        .stat-card h3 {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }

        .stat-card .value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-card .label {
            font-size: 0.85rem;
            color: #888;
        }

        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: #6b7280; }

        .tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 5px;
            margin-bottom: 30px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }

        .tab {
            flex: 1;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .tab-content.active { display: block; }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9rem;
        }

        .data-table th,
        .data-table td {
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        .data-table th {
            background: #f8fafc;
            font-weight: 600;
            color: #374151;
            position: sticky;
            top: 0;
        }

        .data-table tr:hover {
            background: #f8fafc;
        }

        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }

        .status-signaled { background: #fef3c7; color: #d97706; }
        .status-filled { background: #dbeafe; color: #2563eb; }
        .status-completed { background: #d1fae5; color: #065f46; }

        .signal-type-buy { background: #dbeafe; color: #1e40af; }
        .signal-type-sell { background: #fee2e2; color: #dc2626; }

        .filters {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            min-width: 150px;
        }

        .filter-group label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #374151;
            margin-bottom: 5px;
        }

        .filter-group select,
        .filter-group input {
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 0.9rem;
        }

        .date-time-filters {
            display: flex;
            gap: 10px;
            align-items: end;
        }

        .date-time-filters .filter-group {
            min-width: 120px;
        }

        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .btn-secondary {
            background: #6b7280;
        }

        .btn-secondary:hover {
            background: #4b5563;
        }

        .loading {
            text-align: center;
            padding: 50px;
            color: #6b7280;
        }

        .no-data {
            text-align: center;
            padding: 50px;
            color: #6b7280;
            font-style: italic;
        }

        @media (max-width: 768px) {
            .dashboard { padding: 10px; }
            .header { padding: 20px; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; }
            .filters { flex-direction: column; align-items: stretch; }
            .filter-group { min-width: auto; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 MoNo Engine Dashboard</h1>
            <p>Real-time trading signals and performance analytics</p>
            <div id="testMessage" style="margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 8px; font-size: 14px; color: #333;">Initializing...</div>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <h3>Total Signals</h3>
                <div class="value" id="totalSignals">-</div>
                <div class="label">All time</div>
            </div>
            <div class="stat-card">
                <h3>Active Trades</h3>
                <div class="value" id="activeTrades">-</div>
                <div class="label">Currently open</div>
            </div>
            <div class="stat-card">
                <h3>Total PnL</h3>
                <div class="value" id="totalPnL">-</div>
                <div class="label">Realized profit/loss</div>
            </div>
            <div class="stat-card">
                <h3>Win Rate</h3>
                <div class="value" id="winRate">-</div>
                <div class="label">Successful trades</div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('signals')">📡 Signals</div>
            <div class="tab" onclick="switchTab('today')">📅 Today's Trading</div>
            <div class="tab" onclick="switchTab('trades')">📊 All Trades</div>
            <div class="tab" onclick="switchTab('active')">🔄 Active Trades</div>
            <div class="tab" onclick="switchTab('analytics')">📊 Analytics</div>
        </div>

        <div id="signalsTab" class="tab-content active">
            <div class="filters">
                <div class="filter-group">
                    <label>Symbol</label>
                    <select id="signalSymbolFilter" onchange="filterSignals()">
                        <option value="">All Symbols</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Type</label>
                    <select id="signalTypeFilter" onchange="filterSignals()">
                        <option value="">All Types</option>
                        <option value="buy">Buy</option>
                        <option value="sell">Sell</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Status</label>
                    <select id="signalStatusFilter" onchange="filterSignals()">
                        <option value="">All Status</option>
                        <option value="signaled">Signaled</option>
                        <option value="filled">Filled</option>
                    </select>
                </div>
                <div class="date-time-filters">
                    <div class="filter-group">
                        <label>From Date</label>
                        <input type="date" id="signalFromDateFilter" onchange="filterSignals()">
                    </div>
                    <div class="filter-group">
                        <label>To Date</label>
                        <input type="date" id="signalToDateFilter" onchange="filterSignals()">
                    </div>
                </div>
                <button class="btn" onclick="clearSignalFilters()">🗑️ Clear Filters</button>
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
            <table class="data-table" id="signalsTable">
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
                <tbody id="signalsBody">
                    <tr><td colspan="8" class="loading">Loading signals...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="todayTab" class="tab-content">
            <div class="filters">
                <div class="filter-group">
                    <label>Symbol</label>
                    <select id="todaySymbolFilter" onchange="filterTodayTrades()">
                        <option value="">All Symbols</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Status</label>
                    <select id="todayStatusFilter" onchange="filterTodayTrades()">
                        <option value="">All</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>PnL</label>
                    <select id="todayPnlFilter" onchange="filterTodayTrades()">
                        <option value="">All</option>
                        <option value="positive">Profitable</option>
                        <option value="negative">Loss</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Sell Reason</label>
                    <select id="todaySellReasonFilter" onchange="filterTodayTrades()">
                        <option value="">All Reasons</option>
                    </select>
                </div>
                <div class="date-time-filters">
                    <div class="filter-group">
                        <label>From Time</label>
                        <input type="time" id="todayFromTimeFilter" onchange="filterTodayTrades()">
                    </div>
                    <div class="filter-group">
                        <label>To Time</label>
                        <input type="time" id="todayToTimeFilter" onchange="filterTodayTrades()">
                    </div>
                </div>
                <button class="btn" onclick="clearTodayFilters()">🗑️ Clear Filters</button>
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
            <table class="data-table" id="todayTable">
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
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="todayBody">
                    <tr><td colspan="11" class="loading">Loading today's trades...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="tradesTab" class="tab-content">
            <div class="filters">
                <div class="filter-group">
                    <label>Symbol</label>
                    <select id="tradeSymbolFilter" onchange="filterTrades()">
                        <option value="">All Symbols</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>PnL</label>
                    <select id="tradePnlFilter" onchange="filterTrades()">
                        <option value="">All</option>
                        <option value="positive">Profitable</option>
                        <option value="negative">Loss</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Sell Reason</label>
                    <select id="tradeSellReasonFilter" onchange="filterTrades()">
                        <option value="">All Reasons</option>
                    </select>
                </div>
                <div class="date-time-filters">
                    <div class="filter-group">
                        <label>From Date</label>
                        <input type="date" id="tradeFromDateFilter" onchange="filterTrades()">
                    </div>
                    <div class="filter-group">
                        <label>To Date</label>
                        <input type="date" id="tradeToDateFilter" onchange="filterTrades()">
                    </div>
                    <div class="filter-group">
                        <label>From Time</label>
                        <input type="time" id="tradeFromTimeFilter" onchange="filterTrades()">
                    </div>
                    <div class="filter-group">
                        <label>To Time</label>
                        <input type="time" id="tradeToTimeFilter" onchange="filterTrades()">
                    </div>
                </div>
                <button class="btn" onclick="clearTradeFilters()">🗑️ Clear Filters</button>
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
                <button class="btn btn-secondary" onclick="exportTrades()">📥 Export CSV</button>
            </div>
            <table class="data-table" id="tradesTable">
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
                <tbody id="tradesBody">
                    <tr><td colspan="10" class="loading">Loading trades...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="activeTab" class="tab-content">
            <div class="filters">
                <div class="filter-group">
                    <label>Symbol</label>
                    <select id="activeSymbolFilter" onchange="filterActiveTrades()">
                        <option value="">All Symbols</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Buy Reason</label>
                    <select id="activeBuyReasonFilter" onchange="filterActiveTrades()">
                        <option value="">All Reasons</option>
                    </select>
                </div>
                <button class="btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
            <table class="data-table" id="activeTable">
                <thead>
                    <tr>
                        <th>Entry Time</th>
                        <th>Symbol</th>
                        <th>Buy Reason</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>Quantity</th>
                        <th>Unrealized PnL</th>
                        <th>% Change</th>
                    </tr>
                </thead>
                <tbody id="activeBody">
                    <tr><td colspan="8" class="loading">Loading active trades...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="analyticsTab" class="tab-content">
            <div class="stat-card" style="margin-bottom: 30px;">
                <h3>Performance Overview</h3>
                <div id="analyticsContent" class="loading">Loading analytics...</div>
            </div>
        </div>
    </div>

    <script>
        // Simple immediate test
        alert('JavaScript is working!');

        let allSignals = [];
        let allTrades = [];

        // Load data immediately
        console.log('Starting to load data...');
        document.getElementById('testMessage').textContent = 'Starting data load...';

        loadData();

        async function loadData() {
            try {
                console.log('Fetching from API...');
                document.getElementById('testMessage').textContent = 'Fetching from API...';

                const response = await fetch('/api/signals-data');
                console.log('Response received, status:', response.status);

                if (!response.ok) {
                    throw new Error('API error: ' + response.status);
                }

                const responseData = await response.json();
                console.log('JSON parsed successfully');

                // Handle wrapped response format
                const data = responseData.success ? responseData.data : responseData;
                console.log('Data extracted:', data.signals ? data.signals.length : 0, 'signals,', data.trades ? data.trades.length : 0, 'trades');

                allSignals = data.signals || [];
                allTrades = data.trades || [];

                // Update UI
                updateStats();
                updateSignalsTable(allSignals.slice(0, 10)); // Show first 10
                updateTradesTable(allTrades.slice(0, 10)); // Show first 10

                document.getElementById('testMessage').textContent = 'SUCCESS! Loaded ' + allSignals.length + ' signals and ' + allTrades.length + ' trades';
                console.log('UI updated successfully');

            } catch (error) {
                console.error('Load error:', error);
                document.getElementById('testMessage').textContent = 'ERROR: ' + error.message;
                alert('Error: ' + error.message);
            }
        }

        async function refreshData() {
            await loadData();
        }

        function updateStats() {
            const totalSignals = allSignals.length;
            const activeTrades = allTrades.filter(t => !t.exit_time).length;
            const completedTrades = allTrades.filter(t => t.exit_time && t.realized_pnl !== null);
            const totalPnL = completedTrades.reduce((sum, t) => sum + (t.realized_pnl || 0), 0);
            const winningTrades = completedTrades.filter(t => (t.realized_pnl || 0) > 0).length;
            const winRate = completedTrades.length > 0 ? (winningTrades / completedTrades.length * 100).toFixed(1) : '0.0';

            document.getElementById('totalSignals').textContent = totalSignals;
            document.getElementById('activeTrades').textContent = activeTrades;
            document.getElementById('totalPnL').innerHTML = `<span class="${totalPnL >= 0 ? 'positive' : 'negative'}">₹${Math.abs(totalPnL).toLocaleString('en-IN')}</span>`;
            document.getElementById('winRate').innerHTML = `<span class="${parseFloat(winRate) >= 50 ? 'positive' : 'negative'}">${winRate}%</span>`;
        }

        function populateFilters() {
            // Signal filters
            const signalSymbols = [...new Set(allSignals.map(s => s.symbol))].sort();
            const signalSymbolSelect = document.getElementById('signalSymbolFilter');
            signalSymbolSelect.innerHTML = '<option value="">All Symbols</option>';
            signalSymbols.forEach(symbol => {
                const option = document.createElement('option');
                option.value = symbol;
                option.textContent = symbol;
                signalSymbolSelect.appendChild(option);
            });

            // Today's trade filters
            const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
            const todayTrades = allTrades.filter(t => t.entry_time && t.entry_time.startsWith(today));
            const todaySymbols = [...new Set(todayTrades.map(t => t.symbol))].sort();
            const todaySymbolSelect = document.getElementById('todaySymbolFilter');
            todaySymbolSelect.innerHTML = '<option value="">All Symbols</option>';
            todaySymbols.forEach(symbol => {
                const option = document.createElement('option');
                option.value = symbol;
                option.textContent = symbol;
                todaySymbolSelect.appendChild(option);
            });

            const todaySellReasons = [...new Set(todayTrades.map(t => t.sell_reason).filter(r => r))].sort();
            const todaySellReasonSelect = document.getElementById('todaySellReasonFilter');
            todaySellReasonSelect.innerHTML = '<option value="">All Reasons</option>';
            todaySellReasons.forEach(reason => {
                const option = document.createElement('option');
                option.value = reason;
                option.textContent = reason;
                todaySellReasonSelect.appendChild(option);
            });

            // Trade filters
            const tradeSymbols = [...new Set(allTrades.map(t => t.symbol))].sort();
            const tradeSymbolSelect = document.getElementById('tradeSymbolFilter');
            tradeSymbolSelect.innerHTML = '<option value="">All Symbols</option>';
            tradeSymbols.forEach(symbol => {
                const option = document.createElement('option');
                option.value = symbol;
                option.textContent = symbol;
                tradeSymbolSelect.appendChild(option);
            });

            // Sell reason filter
            const sellReasons = [...new Set(allTrades.map(t => t.sell_reason).filter(r => r))].sort();
            const sellReasonSelect = document.getElementById('tradeSellReasonFilter');
            sellReasonSelect.innerHTML = '<option value="">All Reasons</option>';
            sellReasons.forEach(reason => {
                const option = document.createElement('option');
                option.value = reason;
                option.textContent = reason;
                sellReasonSelect.appendChild(option);
            });

            // Active trade filters
            const activeSymbols = [...new Set(allTrades.filter(t => !t.exit_time).map(t => t.symbol))].sort();
            const activeSymbolSelect = document.getElementById('activeSymbolFilter');
            activeSymbolSelect.innerHTML = '<option value="">All Symbols</option>';
            activeSymbols.forEach(symbol => {
                const option = document.createElement('option');
                option.value = symbol;
                option.textContent = symbol;
                activeSymbolSelect.appendChild(option);
            });

            const activeBuyReasons = [...new Set(allTrades.filter(t => !t.exit_time).map(t => t.buy_reason))].sort();
            const activeBuyReasonSelect = document.getElementById('activeBuyReasonFilter');
            activeBuyReasonSelect.innerHTML = '<option value="">All Reasons</option>';
            activeBuyReasons.forEach(reason => {
                const option = document.createElement('option');
                option.value = reason;
                option.textContent = reason;
                activeBuyReasonSelect.appendChild(option);
            });
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
            document.getElementById(tabName + 'Tab').classList.add('active');
            currentTab = tabName;
        }

        function filterSignals() {
            const symbol = document.getElementById('signalSymbolFilter').value;
            const type = document.getElementById('signalTypeFilter').value;
            const status = document.getElementById('signalStatusFilter').value;
            const fromDate = document.getElementById('signalFromDateFilter').value;
            const toDate = document.getElementById('signalToDateFilter').value;

            const filtered = allSignals.filter(signal => {
                if (symbol && signal.symbol !== symbol) return false;
                if (type && signal.signal_type !== type) return false;
                if (status && signal.status !== status) return false;

                // Date filtering
                if (signal.signal_time) {
                    const signalDate = new Date(signal.signal_time);
                    if (fromDate) {
                        const fromDateTime = new Date(fromDate + 'T00:00:00');
                        if (signalDate < fromDateTime) return false;
                    }
                    if (toDate) {
                        const toDateTime = new Date(toDate + 'T23:59:59');
                        if (signalDate > toDateTime) return false;
                    }
                }

                return true;
            });

            updateSignalsTable(filtered);
        }

        function clearSignalFilters() {
            document.getElementById('signalSymbolFilter').value = '';
            document.getElementById('signalTypeFilter').value = '';
            document.getElementById('signalStatusFilter').value = '';
            document.getElementById('signalFromDateFilter').value = '';
            document.getElementById('signalToDateFilter').value = '';
            filterSignals();
        }

        function filterTrades() {
            const symbol = document.getElementById('tradeSymbolFilter').value;
            const pnlFilter = document.getElementById('tradePnlFilter').value;
            const sellReason = document.getElementById('tradeSellReasonFilter').value;
            const fromDate = document.getElementById('tradeFromDateFilter').value;
            const toDate = document.getElementById('tradeToDateFilter').value;
            const fromTime = document.getElementById('tradeFromTimeFilter').value;
            const toTime = document.getElementById('tradeToTimeFilter').value;

            const filtered = allTrades.filter(trade => {
                if (symbol && trade.symbol !== symbol) return false;
                if (pnlFilter === 'positive' && (!trade.realized_pnl || trade.realized_pnl <= 0)) return false;
                if (pnlFilter === 'negative' && (!trade.realized_pnl || trade.realized_pnl > 0)) return false;
                if (sellReason && trade.sell_reason !== sellReason) return false;

                // Date filtering
                if (trade.entry_time) {
                    const tradeDate = new Date(trade.entry_time);
                    if (fromDate) {
                        const fromDateTime = new Date(fromDate + 'T00:00:00');
                        if (tradeDate < fromDateTime) return false;
                    }
                    if (toDate) {
                        const toDateTime = new Date(toDate + 'T23:59:59');
                        if (tradeDate > toDateTime) return false;
                    }

                    // Time filtering (only if date is set)
                    if (fromDate || toDate) {
                        const tradeTime = tradeDate.toTimeString().slice(0, 5); // HH:MM format
                        if (fromTime && tradeTime < fromTime) return false;
                        if (toTime && tradeTime > toTime) return false;
                    }
                }

                return true;
            });

            updateTradesTable(filtered);
        }

        function clearTradeFilters() {
            document.getElementById('tradeSymbolFilter').value = '';
            document.getElementById('tradePnlFilter').value = '';
            document.getElementById('tradeSellReasonFilter').value = '';
            document.getElementById('tradeFromDateFilter').value = '';
            document.getElementById('tradeFromTimeFilter').value = '';
            document.getElementById('tradeToDateFilter').value = '';
            document.getElementById('tradeToTimeFilter').value = '';
            filterTrades();
        }

        function filterTodayTrades() {
            const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
            const symbol = document.getElementById('todaySymbolFilter').value;
            const status = document.getElementById('todayStatusFilter').value;
            const pnlFilter = document.getElementById('todayPnlFilter').value;
            const sellReason = document.getElementById('todaySellReasonFilter').value;
            const fromTime = document.getElementById('todayFromTimeFilter').value;
            const toTime = document.getElementById('todayToTimeFilter').value;

            const filtered = allTrades.filter(trade => {
                // Only today's trades
                if (!trade.entry_time || !trade.entry_time.startsWith(today)) return false;

                if (symbol && trade.symbol !== symbol) return false;

                // Status filter
                if (status === 'active' && trade.exit_time) return false;
                if (status === 'completed' && !trade.exit_time) return false;

                if (pnlFilter === 'positive' && (!trade.realized_pnl || trade.realized_pnl <= 0)) return false;
                if (pnlFilter === 'negative' && (!trade.realized_pnl || trade.realized_pnl > 0)) return false;
                if (sellReason && trade.sell_reason !== sellReason) return false;

                // Time filtering
                if (trade.entry_time) {
                    const tradeTime = new Date(trade.entry_time).toTimeString().slice(0, 5); // HH:MM format
                    if (fromTime && tradeTime < fromTime) return false;
                    if (toTime && tradeTime > toTime) return false;
                }

                return true;
            });

            updateTodayTable(filtered);
        }

        function clearTodayFilters() {
            document.getElementById('todaySymbolFilter').value = '';
            document.getElementById('todayStatusFilter').value = '';
            document.getElementById('todayPnlFilter').value = '';
            document.getElementById('todaySellReasonFilter').value = '';
            document.getElementById('todayFromTimeFilter').value = '';
            document.getElementById('todayToTimeFilter').value = '';
            filterTodayTrades();
        }

        function filterActiveTrades() {
            const symbol = document.getElementById('activeSymbolFilter').value;
            const buyReason = document.getElementById('activeBuyReasonFilter').value;

            const filtered = allTrades.filter(trade => {
                if (!trade.exit_time) {  // Only active trades
                    if (symbol && trade.symbol !== symbol) return false;
                    if (buyReason && trade.buy_reason !== buyReason) return false;
                    return true;
                }
                return false;
            });

            updateActiveTable(filtered);
        }

        function updateSignalsTable(signals) {
            const tbody = document.getElementById('signalsBody');

            if (signals.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="no-data">No signals found</td></tr>';
                return;
            }

            tbody.innerHTML = signals.map(signal => `
                <tr>
                    <td>${new Date(signal.signal_time).toLocaleString()}</td>
                    <td>${signal.symbol}</td>
                    <td><span class="status-badge signal-type-${signal.signal_type}">${signal.signal_type.toUpperCase()}</span></td>
                    <td>${signal.signal_reason}</td>
                    <td>${signal.signal_price ? signal.signal_price.toFixed(2) : '-'}</td>
                    <td>${signal.candle_close ? signal.candle_close.toFixed(2) : '-'}</td>
                    <td><span class="status-badge status-${signal.status}">${signal.status}</span></td>
                    <td>${signal.is_live ? '🔴 LIVE' : '📊 HISTORICAL'}</td>
                </tr>
            `).join('');
        }

        function updateTradesTable(trades) {
            const tbody = document.getElementById('tradesBody');

            if (trades.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10" class="no-data">No trades found</td></tr>';
                return;
            }

            tbody.innerHTML = trades.map(trade => {
                const pnlClass = trade.realized_pnl ? (trade.realized_pnl > 0 ? 'positive' : 'negative') : 'neutral';
                // Show total PnL (not per lot)
                const pnlText = trade.realized_pnl ? `₹${trade.realized_pnl.toLocaleString('en-IN')}` : '-';
                const pnlPercent = trade.realized_pnl && trade.entry_price ?
                    ((trade.exit_price - trade.entry_price) / trade.entry_price * 100).toFixed(2) + '%' : '-';
                // For close price, use exit price for completed trades
                const closePrice = trade.exit_price ? trade.exit_price.toFixed(2) : '-';

                // Display quantity as 900 (45 * 20)
                const displayQuantity = 900;

                return `
                    <tr>
                        <td>${new Date(trade.entry_time).toLocaleString()}</td>
                        <td>${trade.symbol}</td>
                        <td>${trade.buy_reason}</td>
                        <td>${trade.sell_reason || '-'}</td>
                        <td>${trade.entry_price.toFixed(2)}</td>
                        <td>${trade.exit_price ? trade.exit_price.toFixed(2) : '-'}</td>
                        <td>${closePrice}</td>
                        <td>${displayQuantity}</td>
                        <td class="${pnlClass}">${pnlText}</td>
                        <td class="${pnlClass}">${pnlPercent}</td>
                    </tr>
                `;
            }).join('');
        }

        function updateTodayTable(trades) {
            const tbody = document.getElementById('todayBody');

            if (trades.length === 0) {
                tbody.innerHTML = '<tr><td colspan="11" class="no-data">No trades found for today</td></tr>';
                return;
            }

            tbody.innerHTML = trades.map(trade => {
                const pnlClass = trade.realized_pnl ? (trade.realized_pnl > 0 ? 'positive' : 'negative') : 'neutral';
                // Show total PnL (not per lot)
                const pnlText = trade.realized_pnl ? `₹${trade.realized_pnl.toLocaleString('en-IN')}` : '-';
                const pnlPercent = trade.realized_pnl && trade.entry_price ?
                    ((trade.exit_price - trade.entry_price) / trade.entry_price * 100).toFixed(2) + '%' : '-';
                const status = trade.exit_time ? 'Completed' : 'Active';
                // For close price, use exit price for completed trades
                const closePrice = trade.exit_price ? trade.exit_price.toFixed(2) : '-';

                // Display quantity as 900 (45 * 20)
                const displayQuantity = 900;

                return `
                    <tr>
                        <td>${new Date(trade.entry_time).toLocaleString()}</td>
                        <td>${trade.symbol}</td>
                        <td>${trade.buy_reason}</td>
                        <td>${trade.sell_reason || '-'}</td>
                        <td>${trade.entry_price.toFixed(2)}</td>
                        <td>${trade.exit_price ? trade.exit_price.toFixed(2) : '-'}</td>
                        <td>${closePrice}</td>
                        <td>${displayQuantity}</td>
                        <td class="${pnlClass}">${pnlText}</td>
                        <td class="${pnlClass}">${pnlPercent}</td>
                        <td><span class="status-badge status-${status.toLowerCase()}">${status}</span></td>
                    </tr>
                `;
            }).join('');
        }

        function updateActiveTable(trades) {
            const tbody = document.getElementById('activeBody');

            if (trades.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="no-data">No active trades found</td></tr>';
                return;
            }

            tbody.innerHTML = trades.map(trade => {
                // Get current LTP from market data (quotes)
                const symbolKey = trade.symbol + '_BFO'; // Add exchange suffix
                const currentPrice = getCurrentPrice(trade.symbol) || trade.entry_price; // Fallback to entry price

                // Calculate unrealized PnL (total, not per lot)
                const unrealizedPnL = (currentPrice - trade.entry_price) * trade.quantity;
                const pnlClass = unrealizedPnL > 0 ? 'positive' : unrealizedPnL < 0 ? 'negative' : 'neutral';
                const pnlText = `₹${unrealizedPnL.toLocaleString('en-IN')}`;
                const pnlPercent = ((currentPrice - trade.entry_price) / trade.entry_price * 100).toFixed(2) + '%';

                // Display quantity as 900 (45 * 20)
                const displayQuantity = 900;

                return `
                    <tr>
                        <td>${new Date(trade.entry_time).toLocaleString()}</td>
                        <td>${trade.symbol}</td>
                        <td>${trade.buy_reason}</td>
                        <td>${trade.entry_price.toFixed(2)}</td>
                        <td>${currentPrice.toFixed(2)}</td>
                        <td>${displayQuantity}</td>
                        <td class="${pnlClass}">${pnlText}</td>
                        <td class="${pnlClass}">${pnlPercent}</td>
                    </tr>
                `;
            }).join('');
        }

        function getCurrentPrice(symbol) {
            // This function would need to be implemented to get real-time LTP
            // For now, return a placeholder or get from cached quotes
            // In a real implementation, this would fetch from market_data.quotes
            return null; // Will fallback to entry_price
        }

        function updateAnalytics() {
            const analyticsDiv = document.getElementById('analyticsContent');

            if (allTrades.length === 0) {
                analyticsDiv.innerHTML = '<div class="no-data">No trade data available for analytics</div>';
                return;
            }

            const completedTrades = allTrades.filter(t => t.exit_time && t.realized_pnl !== null);
            const totalTrades = completedTrades.length;
            const winningTrades = completedTrades.filter(t => t.realized_pnl > 0).length;
            const losingTrades = totalTrades - winningTrades;
            const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100).toFixed(1) : 0;
            const avgWin = winningTrades > 0 ? completedTrades.filter(t => t.realized_pnl > 0).reduce((sum, t) => sum + t.realized_pnl, 0) / winningTrades : 0;
            const avgLoss = losingTrades > 0 ? completedTrades.filter(t => t.realized_pnl < 0).reduce((sum, t) => sum + t.realized_pnl, 0) / losingTrades : 0;
            const profitFactor = Math.abs(avgLoss) > 0 ? (avgWin / Math.abs(avgLoss)).toFixed(2) : '∞';

            analyticsDiv.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px;">
                    <div style="text-align: center;">
                        <h4>Total Trades</h4>
                        <div style="font-size: 2rem; font-weight: bold; color: #667eea;">${totalTrades}</div>
                    </div>
                    <div style="text-align: center;">
                        <h4>Win Rate</h4>
                        <div style="font-size: 2rem; font-weight: bold; color: ${parseFloat(winRate) >= 50 ? '#10b981' : '#ef4444'};">${winRate}%</div>
                    </div>
                    <div style="text-align: center;">
                        <h4>Avg Win</h4>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">₹${avgWin.toLocaleString('en-IN')}</div>
                    </div>
                    <div style="text-align: center;">
                        <h4>Avg Loss</h4>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #ef4444;">₹${Math.abs(avgLoss).toLocaleString('en-IN')}</div>
                    </div>
                    <div style="text-align: center;">
                        <h4>Profit Factor</h4>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #f59e0b;">${profitFactor}</div>
                    </div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px;">
                    <h4>Performance Insights</h4>
                    <ul style="line-height: 1.6;">
                        <li><strong>Win Rate:</strong> ${winRate}% (${winningTrades} wins, ${losingTrades} losses)</li>
                        <li><strong>Risk/Reward:</strong> 1:${profitFactor} (Profit Factor)</li>
                        <li><strong>Strategy Health:</strong> ${parseFloat(winRate) >= 50 ? 'Good' : parseFloat(winRate) >= 40 ? 'Fair' : 'Needs Improvement'}</li>
                        <li><strong>Recommendation:</strong> ${parseFloat(profitFactor) > 1.5 ? 'Continue' : parseFloat(profitFactor) > 1 ? 'Monitor closely' : 'Review strategy'}</li>
                    </ul>
                </div>
            `;
        }

        function exportTrades() {
            if (allTrades.length === 0) {
                alert('No trade data to export');
                return;
            }

            const csvContent = [
                ['Entry Time', 'Symbol', 'Buy Reason', 'Entry Price', 'Exit Price', 'Quantity', 'PnL Amount', 'PnL %'],
                ...allTrades.map(t => [
                    t.entry_time,
                    t.symbol,
                    t.buy_reason,
                    t.exit_price || '',
                    t.quantity,
                    t.realized_pnl || '',
                    t.realized_pnl && t.entry_price ? ((t.exit_price - t.entry_price) / t.entry_price * 100).toFixed(2) : ''
                ])
            ].map(row => row.join(',')).join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `trading_results_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        }

        function showError(message) {
            // Simple error display
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #ef4444; color: white; padding: 15px; border-radius: 8px; z-index: 1000;';
            errorDiv.textContent = message;
            document.body.appendChild(errorDiv);
            setTimeout(() => document.body.removeChild(errorDiv), 5000);
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>"""