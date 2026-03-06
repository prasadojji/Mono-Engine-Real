#!/usr/bin/env python3
import sqlite3
import sys

def main():
    try:
        conn = sqlite3.connect('mono_engine_data.db')
        cursor = conn.cursor()

        # Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Available tables:')
        for table in tables:
            print(f'  - {table[0]}')

        # Check if trades_signals exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades_signals'")
        if cursor.fetchone():
            print('\ntrades_signals table exists')
            cursor.execute('SELECT COUNT(*) FROM trades_signals')
            count = cursor.fetchone()[0]
            print(f'trades_signals has {count} rows')

            # Get column info
            cursor.execute('PRAGMA table_info(trades_signals)')
            columns = cursor.fetchall()
            print('Columns:', [col[1] for col in columns])
        else:
            print('\ntrades_signals table does NOT exist')

        # Check if trades exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
        if cursor.fetchone():
            print('\ntrades table exists')
            cursor.execute('SELECT COUNT(*) FROM trades')
            count = cursor.fetchone()[0]
            print(f'trades has {count} rows')

            # Get column info
            cursor.execute('PRAGMA table_info(trades)')
            columns = cursor.fetchall()
            print('Columns:', [col[1] for col in columns])
        else:
            print('\ntrades table does NOT exist')

        conn.close()
        print('\nDatabase check completed successfully')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()