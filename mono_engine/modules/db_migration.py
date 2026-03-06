import sqlite3

conn = sqlite3.connect('mono_engine_data.db')
c = conn.cursor()

print("🔧 Running safe migration...")

# Check existing columns
c.execute("PRAGMA table_info(trades)")
existing_cols = {row[1] for row in c.fetchall()}

# Add columns only if missing
columns_to_add = [
    ("buy_reason", "TEXT DEFAULT 'unknown'"),
    ("sell_reason", "TEXT DEFAULT 'unknown'"),
    ("buy_date", "TEXT"),
    ("buy_time", "TEXT"),
    ("sell_date", "TEXT"),
    ("sell_time", "TEXT"),
    ("pnl_rs", "REAL DEFAULT 0"),
    ("symbol_readable", "TEXT")
]

for col_name, col_def in columns_to_add:
    if col_name not in existing_cols:
        try:
            c.execute(f"ALTER TABLE trades ADD COLUMN {col_name} {col_def}")
            print(f"   Added column: {col_name}")
        except Exception as e:
            print(f"   {col_name} already exists or error: {e}")
    else:
        print(f"   Column {col_name} already exists — skipped")

# Create metadata table for delta tracking
c.execute('''
    CREATE TABLE IF NOT EXISTS backtest_metadata (
        symbol TEXT PRIMARY KEY,
        last_processed_bar TEXT,
        last_backtest_run TEXT,
        days_window_used INTEGER DEFAULT 30
    )
''')
print("   backtest_metadata table ready")

# Drop and recreate backtest tables for dual versioning (development migration)
c.execute('DROP TABLE IF EXISTS backtest_results')
c.execute('DROP TABLE IF EXISTS backtest_trades')
print("   Dropped old backtest tables")

# Create backtest results table for caching (dual versioning)
c.execute('''
    CREATE TABLE backtest_results (
        symbol TEXT,
        buy_version TEXT,
        sell_version TEXT,
        total_trades INTEGER DEFAULT 0,
        winning_trades INTEGER DEFAULT 0,
        losing_trades INTEGER DEFAULT 0,
        win_rate REAL DEFAULT 0.0,
        total_pnl REAL DEFAULT 0.0,
        avg_trade_pnl REAL DEFAULT 0.0,
        max_drawdown REAL DEFAULT 0.0,
        buy_reasons TEXT,  -- JSON string of buy reason counts
        sell_reasons TEXT,  -- JSON string of sell reason counts
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (symbol, buy_version, sell_version)
    )
''')
print("   backtest_results table created (dual versioning)")

# Create backtest trades table for detailed trade logs (dual versioning)
c.execute('''
    CREATE TABLE backtest_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        buy_version TEXT,
        sell_version TEXT,
        entry_time TEXT,
        exit_time TEXT,
        entry_price REAL,
        exit_price REAL,
        quantity INTEGER,
        pnl_amount REAL,
        pnl_percent REAL,
        buy_reason TEXT,
        sell_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print("   backtest_trades table created (dual versioning)")

# Create indexes for faster queries
c.execute('CREATE INDEX idx_backtest_trades_symbol_versions ON backtest_trades(symbol, buy_version, sell_version)')
c.execute('CREATE INDEX idx_backtest_trades_time ON backtest_trades(entry_time)')
print("   Indexes created for performance")

conn.commit()
conn.close()

print("\n✅ Migration completed successfully!")
print("You can now run historical backtest (option 3) — it will use delta mode and caching.")
