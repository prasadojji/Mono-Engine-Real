import sqlite3
import pandas as pd

conn = sqlite3.connect('mono_engine_data.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in DB:", [t[0] for t in tables])  # Output: [] if empty

table = 'historical_1min'  # Change if needed
cursor.execute(f"PRAGMA table_info({table});")
columns = cursor.fetchall()
if columns:
    print(f"Fields in {table}:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")  # Name and type
else:
    print(f"No table '{table}' found.")

# Total rows in table
cursor.execute("SELECT COUNT(*) FROM historical_1min")
total_rows = cursor.fetchone()[0]
print(f"Total rows in historical_1min: {total_rows}")

# Rows per symbol (all unique symbols with count)
cursor.execute("SELECT symbol, COUNT(*) FROM historical_1min GROUP BY symbol")
symbol_counts = cursor.fetchall()
print("Rows per symbol:")
for sym, count in symbol_counts:
    print(f"- {sym}: {count}")

symbol_to_check = 'SENSEX 26Feb26 81800 PE'  # Change to your symbol

conn = sqlite3.connect('mono_engine_data.db')

# First 5 bars (oldest)
df_first = pd.read_sql(f"SELECT * FROM historical_1min WHERE symbol = '{symbol_to_check}' ORDER BY timestamp ASC LIMIT 5", conn)
print(f"\nFirst 5 bars for {symbol_to_check}:")
print(df_first)

# Last 5 bars (newest)
df_last = pd.read_sql(f"SELECT * FROM historical_1min WHERE symbol = '{symbol_to_check}' ORDER BY timestamp DESC LIMIT 5", conn)
print(f"\nLast 5 bars for {symbol_to_check}:")
print(df_last)

conn.close()

conn.close()