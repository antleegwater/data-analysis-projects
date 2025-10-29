import pytest
import pandas as pd
from pathlib import Path
import tempfile
from analyzer.visualization import generate_visualizations


def test_correlation_heatmap():
    """Test correlation heatmap generation"""
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'z': [5, 4, 3, 2, 1]
    })

    temp_path = Path(tempfile.gettempdir()) / "test_viz.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {'numeric_cols': ['x', 'y', 'z']}
    analysis = {'correlations': df.corr().to_dict()}

    result = generate_visualizations(str(temp_path), profile, analysis)

    assert 'visualizations' in result
    assert len(result['visualizations']) > 0

    # Verify files exist
    for viz_path in result['visualizations']:
        assert Path(viz_path).exists()
        assert viz_path.endswith('.png')


def test_distribution_plots():
    """Test distribution histogram generation"""
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 50, 55, 60],
        'income': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000]
    })

    temp_path = Path(tempfile.gettempdir()) / "test_dist.parquet"
    df.to_parquet(temp_path, index=False)

    profile = {'numeric_cols': ['age', 'income']}
    analysis = {}

    result = generate_visualizations(str(temp_path), profile, analysis)

    assert any('distribution' in Path(v).stem for v in result['visualizations'])
