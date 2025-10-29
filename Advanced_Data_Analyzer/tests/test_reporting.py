import pytest
from pathlib import Path
from analyzer.reporting import generate_chat_report, generate_detailed_report


def test_chat_report():
    """Test compact chat report generation"""
    profile = {
        'rows': 50000,
        'cols': 12,
        'missing': {'age': 12.0, 'income': 8.0},
        'numeric_cols': ['age', 'income'],
        'categorical_cols': ['city']
    }

    cleaning_result = {
        'imputed_columns': ['age', 'income'],
        'method_used': 'knn'
    }

    outlier_result = {
        'outlier_count': 23,
        'method_used': 'isolation_forest'
    }

    analysis = {
        'statistics': {
            'age': {'mean': 34.2, 'std': 12.1},
            'income': {'mean': 65000, 'std': 15000}
        }
    }

    report = generate_chat_report(profile, cleaning_result, outlier_result, analysis)

    assert '50,000 rows' in report
    assert '12 columns' in report
    assert 'k-NN' in report or 'knn' in report
    assert '23' in report
    # Token efficiency check - should be compact
    assert len(report) < 1500


def test_detailed_report():
    """Test detailed markdown report generation"""
    profile = {
        'rows': 100,
        'cols': 5,
        'missing': {},
        'numeric_cols': ['age'],
        'categorical_cols': ['city']
    }

    result = generate_detailed_report(
        file_name='test.csv',
        profile=profile,
        cleaning_result={'method_used': 'none'},
        outlier_result={'outlier_count': 0},
        analysis={'statistics': {}},
        viz_paths=[]
    )

    assert result['report_path'].endswith('.md')
    assert Path(result['report_path']).exists()

    # Verify content
    content = Path(result['report_path']).read_text()
    assert '# Data Analysis Report' in content
    assert 'test.csv' in content
