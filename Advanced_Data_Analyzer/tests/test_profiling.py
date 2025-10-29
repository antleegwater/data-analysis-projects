import pytest
import pandas as pd
from pathlib import Path
import tempfile
from analyzer.profiling import profile_data


def test_profile_basic_data():
    """Test profiling returns expected structure"""
    # Create test data
    df = pd.DataFrame({
        'age': [25, 30, 35, None, 40],
        'income': [50000, 60000, 70000, 80000, 90000],
        'city': ['NYC', 'LA', 'Chicago', 'NYC', 'LA'],
        'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005']
    })

    temp_path = Path(tempfile.gettempdir()) / "test_profile.parquet"
    df.to_parquet(temp_path, index=False)

    profile = profile_data(str(temp_path))

    assert profile['rows'] == 5
    assert profile['cols'] == 4
    assert 'age' in profile['missing']
    assert profile['missing']['age'] == 20.0  # 1 of 5 = 20%
    assert set(profile['numeric_cols']) == {'age', 'income'}
    assert set(profile['categorical_cols']) == {'city', 'customer_id'}
    assert 'customer_id' in profile['high_cardinality']
    assert profile['dimensionality'] == 'low'


def test_profile_high_dimensional():
    """Test high dimensionality detection"""
    # Create dataset with 12 numeric columns
    df = pd.DataFrame({f'col_{i}': range(10) for i in range(12)})

    temp_path = Path(tempfile.gettempdir()) / "test_high_dim.parquet"
    df.to_parquet(temp_path, index=False)

    profile = profile_data(str(temp_path))

    assert profile['dimensionality'] == 'high'
    assert len(profile['numeric_cols']) == 12
