import sqlite3
import pandas as pd
conn = sqlite3.connect('mono_engine_data.db')
df = pd.read_sql("SELECT * FROM historical_1min WHERE symbol = 'SENSEX 26FEB 83700 CE' LIMIT 10", conn)  # Change symbol
print(df)  # See if bars exist, non-zero prices
conn.close()