"""Data ingestion module supporting multiple file formats."""
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import tempfile


def ingest_file(file_path: str) -> Dict[str, Any]:
    """
    Ingest a data file and return metadata + path to parquet intermediate.

    Args:
        file_path: Path to input file

    Returns:
        Dictionary with:
            - file_path: Path to intermediate parquet file
            - format: Detected file format
            - metadata: Format-specific metadata
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    loaders = {
        '.csv': _load_csv,
        '.json': _load_json,
        '.xlsx': _load_excel,
        '.parquet': _load_parquet
    }

    if suffix not in loaders:
        raise ValueError(f"Unsupported file format: {suffix}")

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    df, metadata = loaders[suffix](file_path)

    # Write to intermediate parquet
    temp_path = Path(tempfile.gettempdir()) / f"ingested_{path.stem}.parquet"
    df.to_parquet(temp_path, index=False)

    return {
        "file_path": str(temp_path),
        "format": suffix[1:],  # Remove leading dot
        "metadata": metadata
    }


def _load_csv(file_path: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Load CSV file."""
    df = pd.read_csv(file_path)
    metadata = {
        "encoding": "utf-8"  # pandas default
    }
    return df, metadata


def _load_json(file_path: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Load JSON file, flattening nested structures."""
    with open(file_path, 'r') as f:
        data = pd.read_json(f)

    # Flatten if nested
    flattened = False
    if len(data) > 0 and any(isinstance(data[col].iloc[0], (dict, list)) for col in data.columns):
        df = pd.json_normalize(data.to_dict('records'))
        flattened = True
    else:
        df = data

    metadata = {"flattened": flattened}
    return df, metadata


def _load_excel(file_path: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Load Excel file (first sheet with data)."""
    xl_file = pd.ExcelFile(file_path)
    sheet_names = xl_file.sheet_names

    # Use first sheet
    df = pd.read_excel(file_path, sheet_name=sheet_names[0])

    metadata = {
        "sheet_names": sheet_names,
        "sheet_used": sheet_names[0]
    }
    return df, metadata


def _load_parquet(file_path: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Load Parquet file."""
    df = pd.read_parquet(file_path)
    metadata = {}
    return df, metadata
