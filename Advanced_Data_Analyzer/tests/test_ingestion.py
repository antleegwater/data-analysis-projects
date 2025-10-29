import pytest
import pandas as pd
from pathlib import Path
from analyzer.ingestion import ingest_file

def test_ingest_csv():
    """Test CSV file ingestion"""
    csv_path = Path(__file__).parent.parent / "resources" / "sample.csv"

    result = ingest_file(str(csv_path))

    assert "file_path" in result
    assert "format" in result
    assert "metadata" in result
    assert result["format"] == "csv"
    assert Path(result["file_path"]).exists()

    # Verify data was written
    df = pd.read_parquet(result["file_path"])
    assert len(df) > 0


def test_ingest_json():
    """Test JSON file ingestion"""
    json_path = Path(__file__).parent.parent / "resources" / "sample.json"

    result = ingest_file(str(json_path))

    assert result["format"] == "json"
    assert Path(result["file_path"]).exists()

    df = pd.read_parquet(result["file_path"])
    assert len(df) > 0


def test_unsupported_format():
    """Test unsupported file format raises error"""
    with pytest.raises(ValueError, match="Unsupported file format"):
        ingest_file("test.txt")
