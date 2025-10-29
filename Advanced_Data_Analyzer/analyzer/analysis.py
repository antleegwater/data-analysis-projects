"""Statistical analysis module."""
import pandas as pd
from typing import Dict, Any


def analyze_data(file_path: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform statistical analysis on the dataset.

    Args:
        file_path: Path to parquet file
        profile: Profiling results dictionary

    Returns:
        Dictionary with:
            - statistics: Per-column descriptive stats
            - correlations: Correlation matrix for numeric columns
            - categorical_summary: Frequency counts for categorical columns
    """
    df = pd.read_parquet(file_path)

    result = {
        'statistics': {},
        'correlations': None,
        'categorical_summary': {}
    }

    # Descriptive statistics for numeric columns
    for col in profile['numeric_cols']:
        stats = df[col].describe()
        result['statistics'][col] = {
            'mean': round(stats['mean'], 2),
            'std': round(stats['std'], 2),
            'min': round(stats['min'], 2),
            'max': round(stats['max'], 2),
            'median': round(df[col].median(), 2)
        }

    # Correlation matrix
    if len(profile['numeric_cols']) >= 2:
        corr_matrix = df[profile['numeric_cols']].corr()
        result['correlations'] = corr_matrix.to_dict()

    # Categorical summaries (top 10 values)
    for col in profile['categorical_cols']:
        if col not in profile.get('high_cardinality', []):
            value_counts = df[col].value_counts().head(10)
            result['categorical_summary'][col] = {
                str(k): int(v) for k, v in value_counts.items()
            }

    return result
