"""Data profiling module for analyzing dataset characteristics."""
import pandas as pd
from typing import Dict, Any


def profile_data(file_path: str) -> Dict[str, Any]:
    """
    Profile a dataset to understand its structure and quality.

    Args:
        file_path: Path to parquet file

    Returns:
        Dictionary with profiling results:
            - rows: Number of rows
            - cols: Number of columns
            - missing: Dict of {column: percentage_missing}
            - numeric_cols: List of numeric column names
            - categorical_cols: List of categorical column names
            - date_cols: List of date column names
            - high_cardinality: List of high-cardinality columns (>50 unique)
            - dimensionality: 'low' (<10 numeric) or 'high' (>=10 numeric)
    """
    df = pd.read_parquet(file_path)

    # Basic dimensions
    rows, cols = df.shape

    # Missing values
    missing = {}
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            missing[col] = round((missing_count / rows) * 100, 1)

    # Column types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Date columns (datetime types or 'date'/'time' in name)
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    date_cols.extend([col for col in df.columns
                      if ('date' in col.lower() or 'time' in col.lower())
                      and col not in date_cols])

    # High cardinality (>50 unique values or >80% unique for small datasets)
    high_cardinality = []
    for col in categorical_cols:
        n_unique = df[col].nunique()
        unique_ratio = n_unique / rows if rows > 0 else 0
        # Flag as high cardinality if >50 unique OR >80% unique (likely ID column)
        if n_unique > 50 or (unique_ratio > 0.8 and n_unique > 2):
            high_cardinality.append(col)

    # Dimensionality
    dimensionality = 'high' if len(numeric_cols) >= 10 else 'low'

    return {
        'rows': rows,
        'cols': cols,
        'missing': missing,
        'numeric_cols': numeric_cols,
        'categorical_cols': categorical_cols,
        'date_cols': date_cols,
        'high_cardinality': high_cardinality,
        'dimensionality': dimensionality
    }
