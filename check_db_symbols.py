import sqlite3
conn = sqlite3.connect('mono_engine_data.db')
c = conn.cursor()

# Get symbols excluding _51 (BSE index)
c.execute("SELECT DISTINCT symbol FROM historical_1min WHERE symbol NOT LIKE '%_51%' ORDER BY symbol LIMIT 10")
symbols = [row[0] for row in c.fetchall()]

print("Available symbols (excluding BSE index):")
for symbol in symbols:
    print(f"  {symbol}")

# Check data for first symbol
if symbols:
    symbol = symbols[0]
    c.execute(f"SELECT COUNT(*) FROM historical_1min WHERE symbol = '{symbol}'")
    count = c.fetchone()[0]
    print(f"\nData points for {symbol}: {count}")

    # Check date range
    c.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM historical_1min WHERE symbol = '{symbol}'")
    min_date, max_date = c.fetchone()
    print(f"Date range: {min_date} to {max_date}")

conn.close()