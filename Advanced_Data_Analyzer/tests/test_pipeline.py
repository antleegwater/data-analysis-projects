import pytest
from pathlib import Path
from analyze import analyze_file


def test_full_pipeline_csv():
    """Test complete pipeline with CSV file"""
    csv_path = Path(__file__).parent.parent / "resources" / "sample.csv"

    result = analyze_file(str(csv_path))

    assert 'chat_report' in result
    assert 'detailed_report_path' in result
    assert 'visualizations' in result

    # Verify report contains key info
    assert 'rows' in result['chat_report']
    assert Path(result['detailed_report_path']).exists()


def test_pipeline_with_refinement():
    """Test pipeline with ML refinement"""
    csv_path = Path(__file__).parent.parent / "resources" / "sample.csv"

    result = analyze_file(str(csv_path), apply_ml_cleaning=True)

    assert result is not None
