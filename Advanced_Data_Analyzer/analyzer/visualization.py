"""Visualization module for generating charts."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
from pathlib import Path
import tempfile


def generate_visualizations(file_path: str, profile: Dict[str, Any],
                           analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate visualizations based on data characteristics.

    Args:
        file_path: Path to parquet file
        profile: Profiling results dictionary
        analysis: Analysis results dictionary

    Returns:
        Dictionary with:
            - visualizations: List of paths to generated PNG files
    """
    df = pd.read_parquet(file_path)
    reports_dir = Path.cwd() / "reports"
    reports_dir.mkdir(exist_ok=True)
    visualizations = []

    # Correlation heatmap (if multiple numeric columns)
    if len(profile['numeric_cols']) >= 2 and analysis.get('correlations'):
        viz_path = reports_dir / "correlation_heatmap.png"
        _create_correlation_heatmap(analysis['correlations'], viz_path)
        visualizations.append(str(viz_path))

    # Distribution plots for numeric columns
    if profile['numeric_cols']:
        viz_path = reports_dir / "distributions.png"
        _create_distribution_plots(df, profile['numeric_cols'], viz_path)
        visualizations.append(str(viz_path))

    # Categorical bar charts (if low cardinality)
    low_card_cats = [col for col in profile.get('categorical_cols', [])
                     if col not in profile.get('high_cardinality', [])]
    if low_card_cats:
        viz_path = reports_dir / "categorical_distributions.png"
        _create_categorical_plots(df, low_card_cats[:4], viz_path)
        visualizations.append(str(viz_path))

    return {'visualizations': visualizations}


def _create_correlation_heatmap(correlations: Dict, output_path: Path):
    """Create correlation heatmap."""
    corr_df = pd.DataFrame(correlations)

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1, fmt='.2f')
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _create_distribution_plots(df: pd.DataFrame, numeric_cols: List[str],
                               output_path: Path):
    """Create distribution histograms."""
    n_cols = min(4, len(numeric_cols))
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for idx, col in enumerate(numeric_cols[:4]):
        axes[idx].hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
        axes[idx].set_title(f'Distribution of {col}')
        axes[idx].set_xlabel(col)
        axes[idx].set_ylabel('Frequency')
        axes[idx].grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(len(numeric_cols[:4]), 4):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _create_categorical_plots(df: pd.DataFrame, categorical_cols: List[str],
                              output_path: Path):
    """Create categorical bar charts."""
    n_cols = min(4, len(categorical_cols))
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, col in enumerate(categorical_cols[:4]):
        value_counts = df[col].value_counts().head(10)
        axes[idx].barh(range(len(value_counts)), value_counts.values)
        axes[idx].set_yticks(range(len(value_counts)))
        axes[idx].set_yticklabels(value_counts.index)
        axes[idx].set_title(f'Top Values in {col}')
        axes[idx].set_xlabel('Count')
        axes[idx].grid(True, alpha=0.3, axis='x')

    # Hide unused subplots
    for idx in range(len(categorical_cols[:4]), 4):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
