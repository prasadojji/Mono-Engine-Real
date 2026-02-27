import sqlite3
import pandas as pd

conn = sqlite3.connect('mono_engine_data.db')
cursor = conn.cursor()

# Step 2: List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in DB:", [t[0] for t in tables])

# Step 3: List fields for historical_1min
table_name = 'historical_1min'
cursor.execute(f"PRAGMA table_info({table_name});")
columns = cursor.fetchall()
if columns:
    print(f"Fields in {table_name}:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
else:
    print(f"Table '{table_name}' not found.")

# Step 4: Total rows
cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
total_rows = cursor.fetchone()[0]
print(f"Total rows in {table_name}: {total_rows}")

# Step 5: Rows per symbol
cursor.execute(f"SELECT symbol, COUNT(*) FROM {table_name} GROUP BY symbol")
symbol_counts = cursor.fetchall()
print("Rows per symbol:")
for sym, count in symbol_counts:
    print(f"- {sym}: {count}")

# Step 6: Sample for one symbol
symbol_to_check = 'SENSEX 26Feb26 81800 PE'  # Example from your output
df_first = pd.read_sql(f"SELECT * FROM {table_name} WHERE symbol = '{symbol_to_check}' ORDER BY timestamp ASC LIMIT 5", conn)
print(f"\nFirst 5 bars for {symbol_to_check}:")
print(df_first)

df_last = pd.read_sql(f"SELECT * FROM {table_name} WHERE symbol = '{symbol_to_check}' ORDER BY timestamp DESC LIMIT 5", conn)
print(f"\nLast 5 bars for {symbol_to_check}:")
print(df_last)

conn.close()