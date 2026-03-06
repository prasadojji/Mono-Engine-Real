"""
Core data utilities for safe data conversion and JSON serialization.
Provides functions to handle various data types safely for web API responses.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Any, Optional, Union


def safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Safely convert a value to float, handling NaN, inf, and invalid types.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    if value is None:
        return default

    try:
        # Handle pandas NaN and numpy types
        if pd.isna(value) or (isinstance(value, str) and value.lower() in ['nan', 'inf', '-inf', 'none', '']):
            return default

        # Convert to float
        result = float(value)

        # Check for infinity
        if not np.isfinite(result):
            return default

        return result
    except (ValueError, TypeError, OverflowError):
        return default


def safe_int(value: Any, default: Optional[int] = 0) -> Optional[int]:
    """
    Safely convert a value to int, handling NaN, inf, and invalid types.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Int value or default
    """
    if value is None:
        return default

    try:
        # Handle pandas NaN and numpy types
        if pd.isna(value) or (isinstance(value, str) and value.lower() in ['nan', 'inf', '-inf', 'none', '']):
            return default

        # Convert to int
        result = int(float(value))  # Convert through float to handle strings like "123.0"

        return result
    except (ValueError, TypeError, OverflowError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert a value to string.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        String value or default
    """
    if value is None:
        return default

    try:
        # Handle pandas NaN
        if pd.isna(value):
            return default

        return str(value)
    except Exception:
        return default


def safe_datetime_str(value: Any, default: Optional[str] = None) -> Optional[str]:
    """
    Safely convert datetime-like values to ISO string format.

    Args:
        value: Datetime value to convert
        default: Default value if conversion fails

    Returns:
        ISO formatted datetime string or default
    """
    if value is None or pd.isna(value):
        return default

    try:
        # Handle pandas Timestamp
        if hasattr(value, 'isoformat'):
            return value.isoformat()

        # Handle datetime objects
        if isinstance(value, (datetime, date)):
            return value.isoformat()

        # Handle string timestamps
        if isinstance(value, str):
            # Try to parse and reformat
            parsed = pd.to_datetime(value)
            if pd.notna(parsed):
                return parsed.isoformat()

        return default
    except Exception:
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """
    Safely convert a value to boolean.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Boolean value or default
    """
    if value is None or pd.isna(value):
        return default

    try:
        # Handle various boolean representations
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']

        return bool(value)
    except Exception:
        return default


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitize a pandas DataFrame for JSON serialization.
    Converts all columns to JSON-serializable types.

    Args:
        df: DataFrame to sanitize

    Returns:
        Sanitized DataFrame
    """
    if df.empty:
        return df

    sanitized = df.copy()

    # Convert object columns that might contain mixed types
    for col in sanitized.columns:
        if sanitized[col].dtype == 'object':
            # Try to convert to more specific types where possible
            try:
                # Check if column contains dates
                if col.lower().endswith(('_time', '_date')):
                    sanitized[col] = sanitized[col].apply(safe_datetime_str)
                else:
                    # For other object columns, ensure they're strings
                    sanitized[col] = sanitized[col].apply(lambda x: safe_str(x, ""))
            except Exception:
                # Fallback to string conversion
                sanitized[col] = sanitized[col].apply(lambda x: safe_str(x, ""))

    return sanitized


def dataframe_to_json_serializable(df: pd.DataFrame) -> list:
    """
    Convert a pandas DataFrame to a list of JSON-serializable dictionaries.

    Args:
        df: DataFrame to convert

    Returns:
        List of dictionaries safe for JSON serialization
    """
    if df.empty:
        return []

    # Sanitize the dataframe first
    sanitized_df = sanitize_dataframe(df)

    # Convert to records and ensure all values are JSON-serializable
    records = sanitized_df.to_dict('records')

    # Final pass to ensure all values are JSON-serializable
    serializable_records = []
    for record in records:
        serializable_record = {}
        for key, value in record.items():
            # Apply safe conversions based on key patterns
            if key.lower().endswith(('_time', '_date')):
                serializable_record[key] = safe_datetime_str(value)
            elif key.lower() in ['price', 'amount', 'pnl', 'realized_pnl', 'entry_price', 'exit_price']:
                serializable_record[key] = safe_float(value)
            elif key.lower() in ['quantity', 'lot_size', 'is_live', 'is_historical']:
                serializable_record[key] = safe_int(value)
            else:
                serializable_record[key] = safe_str(value, "")

        serializable_records.append(serializable_record)

    return serializable_records


def validate_json_serializable(data: Any) -> bool:
    """
    Validate that data is JSON serializable.

    Args:
        data: Data to validate

    Returns:
        True if data is JSON serializable, False otherwise
    """
    try:
        import json
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def make_json_response(data: Any, success: bool = True, message: str = "") -> dict:
    """
    Create a standardized JSON response.

    Args:
        data: Response data
        success: Whether the request was successful
        message: Optional message

    Returns:
        Standardized response dictionary
    """
    response = {
        'success': success,
        'data': data
    }

    if message:
        response['message'] = message

    return response