import sqlite3
import pandas as pd

conn = sqlite3.connect('mono_engine_data.db')

# Check the structure of the trades table
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(trades)")
columns = cursor.fetchall()
print("Trades table columns:")
for col in columns:
    print(f"  {col}")

print("\nFirst 10 trades:")
df = pd.read_sql("SELECT * FROM trades LIMIT 10", conn)
print(df)

print("\nChecking for corrupted entry_price values:")
corrupted_df = pd.read_sql("""
    SELECT trade_id, symbol, entry_price, typeof(entry_price) as type
    FROM trades
    WHERE entry_price IN ('fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl')
    LIMIT 20
""", conn)
print(corrupted_df)

conn.close()