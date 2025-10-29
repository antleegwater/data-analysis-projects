"""Data cleaning module with intelligent imputation and outlier detection."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import tempfile
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


def impute_missing(file_path: str, profile: Dict[str, Any],
                   method: str = 'auto', impute_threshold: float = 30.0) -> Dict[str, Any]:
    """
    Impute missing values using appropriate method based on data characteristics.

    Args:
        file_path: Path to parquet file
        profile: Profiling results dictionary
        method: 'auto', 'simple', 'knn', or 'random_forest'
        impute_threshold: Maximum missing percentage to impute (default: 30.0)

    Returns:
        Dictionary with:
            - file_path: Path to cleaned parquet file
            - imputed_columns: List of columns that were imputed
            - skipped_columns: List of columns skipped (too much missing)
            - method_used: Imputation method applied
    """
    df = pd.read_parquet(file_path)

    if not profile['missing']:
        # No missing values
        return {
            'file_path': file_path,
            'imputed_columns': [],
            'skipped_columns': [],
            'method_used': 'none'
        }

    # Filter columns based on threshold
    cols_to_impute = {col: pct for col, pct in profile['missing'].items()
                      if pct <= impute_threshold}
    skipped_columns = {col: pct for col, pct in profile['missing'].items()
                       if pct > impute_threshold}

    if not cols_to_impute:
        # All columns exceed threshold - skip imputation
        return {
            'file_path': file_path,
            'imputed_columns': [],
            'skipped_columns': list(skipped_columns.keys()),
            'method_used': 'none'
        }

    # Determine method if auto (based on max missing % in cols_to_impute)
    if method == 'auto':
        max_missing_pct = max(cols_to_impute.values())
        if max_missing_pct < 5:
            method = 'simple'
        elif max_missing_pct < 15:
            method = 'knn'
        else:
            method = 'random_forest'

    # Update profile to only include columns we're imputing
    impute_profile = profile.copy()
    impute_profile['missing'] = cols_to_impute

    if method == 'simple':
        df = _simple_impute(df, impute_profile)
    elif method == 'knn':
        df = _knn_impute(df, impute_profile)
    elif method == 'random_forest':
        df = _random_forest_impute(df, impute_profile)
    else:
        raise ValueError(f"Unknown imputation method: {method}")

    # Write cleaned data
    temp_path = Path(tempfile.gettempdir()) / f"cleaned_{Path(file_path).stem}.parquet"
    df.to_parquet(temp_path, index=False)

    return {
        'file_path': str(temp_path),
        'imputed_columns': list(cols_to_impute.keys()),
        'skipped_columns': list(skipped_columns.keys()),
        'method_used': method
    }


def _simple_impute(df: pd.DataFrame, profile: Dict[str, Any]) -> pd.DataFrame:
    """Simple median/mode imputation."""
    df = df.copy()

    # Numeric: median
    for col in profile['numeric_cols']:
        if col in profile['missing']:
            df[col] = df[col].fillna(df[col].median())

    # Categorical: mode
    for col in profile['categorical_cols']:
        if col in profile['missing']:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])

    return df


def _knn_impute(df: pd.DataFrame, profile: Dict[str, Any]) -> pd.DataFrame:
    """k-NN imputation for numeric columns."""
    df = df.copy()

    # Only impute numeric columns with k-NN
    numeric_cols = profile['numeric_cols']
    if numeric_cols:
        imputer = KNNImputer(n_neighbors=5)
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

    # Simple imputation for categorical
    for col in profile['categorical_cols']:
        if col in profile['missing']:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])

    return df


def _random_forest_impute(df: pd.DataFrame, profile: Dict[str, Any]) -> pd.DataFrame:
    """Random Forest imputation (placeholder - using k-NN for now)."""
    # For MVP, use k-NN as fallback
    # Full RF imputation requires iterative approach
    return _knn_impute(df, profile)


def detect_outliers(file_path: str, profile: Dict[str, Any],
                    method: str = 'auto') -> Dict[str, Any]:
    """
    Detect outliers using appropriate method based on dimensionality.

    Args:
        file_path: Path to parquet file
        profile: Profiling results dictionary
        method: 'auto', 'iqr', 'knn', or 'isolation_forest'

    Returns:
        Dictionary with:
            - outlier_indices: List of row indices flagged as outliers
            - method_used: Detection method applied
            - outlier_count: Number of outliers detected
    """
    df = pd.read_parquet(file_path)

    numeric_cols = profile['numeric_cols']
    if not numeric_cols:
        return {
            'outlier_indices': [],
            'method_used': 'none',
            'outlier_count': 0
        }

    # Determine method if auto
    if method == 'auto':
        n_numeric = len(numeric_cols)
        if n_numeric < 5:
            method = 'iqr'
        elif n_numeric < 10:
            method = 'knn'
        else:
            method = 'isolation_forest'

    if method == 'iqr':
        outlier_indices = _iqr_outliers(df, numeric_cols)
    elif method == 'knn':
        outlier_indices = _knn_outliers(df, numeric_cols)
    elif method == 'isolation_forest':
        outlier_indices = _isolation_forest_outliers(df, numeric_cols)
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")

    return {
        'outlier_indices': outlier_indices,
        'method_used': method,
        'outlier_count': len(outlier_indices)
    }


def _iqr_outliers(df: pd.DataFrame, numeric_cols: List[str]) -> List[int]:
    """IQR method for univariate outlier detection."""
    outlier_indices = set()

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
        outlier_indices.update(outliers)

    return sorted(list(outlier_indices))


def _knn_outliers(df: pd.DataFrame, numeric_cols: List[str]) -> List[int]:
    """k-NN distance method for multivariate outlier detection."""
    X = df[numeric_cols].dropna()

    if len(X) < 10:
        return []  # Not enough data

    lof = LocalOutlierFactor(n_neighbors=5, contamination=0.1)
    outlier_labels = lof.fit_predict(X)

    # -1 indicates outlier
    outlier_indices = X.index[outlier_labels == -1].tolist()

    return sorted(outlier_indices)


def _isolation_forest_outliers(df: pd.DataFrame, numeric_cols: List[str]) -> List[int]:
    """Isolation Forest for high-dimensional outlier detection."""
    X = df[numeric_cols].dropna()

    if len(X) < 10:
        return []

    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    outlier_labels = iso_forest.fit_predict(X)

    # -1 indicates outlier
    outlier_indices = X.index[outlier_labels == -1].tolist()

    return sorted(outlier_indices)
