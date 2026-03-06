"""
Database utilities for safe database operations and connection management.
Provides centralized database access with proper error handling.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import os


class DatabaseConnection:
    """Context manager for database connections with proper error handling."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            return self.connection
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass  # Ignore errors when closing


def get_database_path() -> str:
    """
    Get the database path from configuration or default location.

    Returns:
        Path to the database file
    """
    # Try to get from environment variable first
    db_path = os.getenv('MONO_ENGINE_DB_PATH')

    if not db_path:
        # Default path
        db_path = 'c:\\MoNo_Engine\\mono_engine_data.db'

    return db_path


def validate_database_connection(db_path: str) -> bool:
    """
    Validate that the database connection works.

    Args:
        db_path: Path to the database file

    Returns:
        True if connection is valid, False otherwise
    """
    try:
        with DatabaseConnection(db_path) as conn:
            # Try a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception:
        return False


def safe_sql_query(db_path: str, query: str, params: Optional[tuple] = None,
                  parse_dates: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Execute a SQL query safely with proper error handling.

    Args:
        db_path: Path to the database file
        query: SQL query string
        params: Query parameters
        parse_dates: Columns to parse as dates

    Returns:
        DataFrame with query results

    Raises:
        Exception: If query fails
    """
    try:
        with DatabaseConnection(db_path) as conn:
            if params:
                df = pd.read_sql_query(query, conn, params=params, parse_dates=parse_dates)
            else:
                df = pd.read_sql_query(query, conn, parse_dates=parse_dates)

            return df

    except Exception as e:
        raise Exception(f"Database query failed: {e}")


def get_table_info(db_path: str, table_name: str) -> Dict[str, Any]:
    """
    Get information about a database table.

    Args:
        db_path: Path to the database file
        table_name: Name of the table

    Returns:
        Dictionary with table information
    """
    try:
        with DatabaseConnection(db_path) as conn:
            # Get column information
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            return {
                'table_name': table_name,
                'columns': [{'name': col[1], 'type': col[2]} for col in columns],
                'row_count': row_count
            }

    except Exception as e:
        raise Exception(f"Failed to get table info for {table_name}: {e}")


def get_database_stats(db_path: str) -> Dict[str, Any]:
    """
    Get overall database statistics.

    Args:
        db_path: Path to the database file

    Returns:
        Dictionary with database statistics
    """
    try:
        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            stats = {
                'database_path': db_path,
                'tables': {},
                'total_records': 0
            }

            for table in tables:
                try:
                    table_info = get_table_info(db_path, table)
                    stats['tables'][table] = table_info
                    stats['total_records'] += table_info['row_count']
                except Exception:
                    # Skip tables we can't access
                    continue

            return stats

    except Exception as e:
        raise Exception(f"Failed to get database stats: {e}")


def execute_safe_query(db_path: str, query: str, params: Optional[tuple] = None) -> int:
    """
    Execute a safe database operation (INSERT, UPDATE, DELETE).

    Args:
        db_path: Path to the database file
        query: SQL query string
        params: Query parameters

    Returns:
        Number of affected rows

    Raises:
        Exception: If operation fails
    """
    try:
        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            conn.commit()
            return cursor.rowcount

    except Exception as e:
        raise Exception(f"Database operation failed: {e}")


def check_table_exists(db_path: str, table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        db_path: Path to the database file
        table_name: Name of the table

    Returns:
        True if table exists, False otherwise
    """
    try:
        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return cursor.fetchone() is not None

    except Exception:
        return False