import sqlite3
import pandas as pd

DB_PATH = 'mono_engine_data.db'

conn = sqlite3.connect(DB_PATH)

# Check if table exists and row count
row_count = pd.read_sql("SELECT COUNT(*) as cnt FROM historical_1min", conn)['cnt'][0]
print(f"Total rows in historical_1min: {row_count}")

if row_count > 0:
    # Sample data
    sample = pd.read_sql("SELECT * FROM historical_1min LIMIT 10", conn)
    print("\nFirst 10 rows:")
    print(sample)
    
    # Summary by symbol
    summary = pd.read_sql("""
        SELECT 
            symbol,
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest,
            COUNT(*) as rows
        FROM historical_1min
        GROUP BY symbol
        ORDER BY rows DESC
        LIMIT 10
    """, conn)
    print("\nTop 10 symbols by row count:")
    print(summary)

else:
    print("Table is empty or does not exist.")

conn.close()