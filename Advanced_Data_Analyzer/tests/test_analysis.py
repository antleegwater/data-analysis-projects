import pytest
import pandas as pd
from pathlib import Path
import tempfile
from analyzer.analysis import analyze_data


def test_basic_analysis():
    """Test basic statistical analysis"""
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'income': [50000, 60000, 70000, 80000, 90000],
        'city': ['NYC', 'LA', 'Chicago', 'NYC', 'LA']
    })

    temp_path = Path(tempfile.gettempdir()) / "test_analysis.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {
        'numeric_cols': ['age', 'income'],
        'categorical_cols': ['city']
    }

    result = analyze_data(str(temp_path), profile)

    assert 'statistics' in result
    assert 'correlations' in result
    assert 'age' in result['statistics']
    assert 'mean' in result['statistics']['age']


def test_correlation_analysis():
    """Test correlation matrix generation"""
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],  # Perfect correlation with x
        'z': [5, 4, 3, 2, 1]    # Perfect negative correlation with x
    })

    temp_path = Path(tempfile.gettempdir()) / "test_corr.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {
        'numeric_cols': ['x', 'y', 'z'],
        'categorical_cols': []
    }

    result = analyze_data(str(temp_path), profile)

    assert result['correlations'] is not None
    assert abs(result['correlations']['x']['y'] - 1.0) < 0.01
