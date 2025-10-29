import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
from analyzer.cleaning import impute_missing, detect_outliers


def test_simple_imputation():
    """Test simple median/mode imputation for <5% missing"""
    df = pd.DataFrame({
        'age': [25, 30, 35, np.nan, 40],  # 20% missing
        'income': [50000, 60000, np.nan, 80000, 90000],  # 20% missing
        'city': ['NYC', 'LA', None, 'NYC', 'LA']  # 20% missing
    })

    temp_path = Path(tempfile.gettempdir()) / "test_simple.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {
        'missing': {'age': 20.0, 'income': 20.0, 'city': 20.0},
        'numeric_cols': ['age', 'income'],
        'categorical_cols': ['city']
    }

    result = impute_missing(str(temp_path), profile, method='simple')

    assert Path(result['file_path']).exists()
    assert 'imputed_columns' in result

    df_clean = pd.read_parquet(result['file_path'])
    assert df_clean['age'].isnull().sum() == 0
    assert df_clean['income'].isnull().sum() == 0
    assert df_clean['city'].isnull().sum() == 0


def test_knn_imputation():
    """Test k-NN imputation for 5-15% missing"""
    df = pd.DataFrame({
        'age': [25, 30, 35, np.nan, 40, 45, 50],
        'income': [50000, 60000, 70000, 80000, 90000, np.nan, 110000],
        'score': [85, 90, 88, 92, np.nan, 94, 96]
    })

    temp_path = Path(tempfile.gettempdir()) / "test_knn.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {
        'missing': {'age': 14.3, 'income': 14.3, 'score': 14.3},
        'numeric_cols': ['age', 'income', 'score'],
        'categorical_cols': []
    }

    result = impute_missing(str(temp_path), profile, method='knn')

    df_clean = pd.read_parquet(result['file_path'])
    assert df_clean.isnull().sum().sum() == 0


def test_iqr_outlier_detection():
    """Test IQR outlier detection for low-dimensional data"""
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 150],  # 150 is outlier
        'income': [50000, 60000, 70000, 80000, 90000, 500000]  # 500k is outlier
    })

    temp_path = Path(tempfile.gettempdir()) / "test_outliers.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {
        'numeric_cols': ['age', 'income'],
        'dimensionality': 'low'
    }

    result = detect_outliers(str(temp_path), profile, method='iqr')

    assert 'outlier_indices' in result
    assert len(result['outlier_indices']) > 0
    assert result['method_used'] == 'iqr'


def test_isolation_forest_outliers():
    """Test Isolation Forest for high-dimensional data"""
    # Create dataset with 10 features
    np.random.seed(42)
    normal_data = np.random.randn(100, 10)
    outlier_data = np.random.randn(5, 10) * 5  # Outliers with larger variance

    data = np.vstack([normal_data, outlier_data])
    df = pd.DataFrame(data, columns=[f'feature_{i}' for i in range(10)])

    temp_path = Path(tempfile.gettempdir()) / "test_isolation.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {
        'numeric_cols': df.columns.tolist(),
        'dimensionality': 'high'
    }

    result = detect_outliers(str(temp_path), profile, method='isolation_forest')

    assert 'outlier_indices' in result
    assert result['method_used'] == 'isolation_forest'
