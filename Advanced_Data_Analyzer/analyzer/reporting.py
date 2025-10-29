"""Reporting module for generating analysis reports."""
from typing import Dict, Any, List
from pathlib import Path
import tempfile
from datetime import datetime


def generate_chat_report(profile: Dict[str, Any],
                        cleaning_result: Dict[str, Any],
                        outlier_result: Dict[str, Any],
                        analysis: Dict[str, Any]) -> str:
    """
    Generate compact chat report (500-800 tokens).

    Args:
        profile: Profiling results
        cleaning_result: Cleaning results
        outlier_result: Outlier detection results
        analysis: Analysis results

    Returns:
        Formatted markdown string
    """
    lines = []

    # Data Overview
    lines.append("## Data Overview")
    lines.append(f"- {profile['rows']:,} rows × {profile['cols']} columns")

    # Data Quality
    if profile['missing'] or outlier_result['outlier_count'] > 0:
        lines.append("\n## Data Quality")
        if profile['missing']:
            missing_summary = ', '.join([f"{col} ({pct}%)"
                                        for col, pct in list(profile['missing'].items())[:3]])
            max_missing = max(profile['missing'].values())

            # Add warning icon for high missing rates
            warning = ""
            if max_missing >= 30:
                warning = " ⚠️ CRITICAL - too sparse for reliable imputation"
            elif max_missing >= 15:
                warning = " ⚠️ HIGH - recommend ML imputation"
            elif max_missing >= 5:
                warning = " ⚠️ MODERATE - consider k-NN imputation"

            lines.append(f"- Missing: {missing_summary}{warning}")
        if outlier_result['outlier_count'] > 0:
            lines.append(f"- Outliers: {outlier_result['outlier_count']} flagged ({outlier_result['method_used']})")

    # Cleaning Applied
    if cleaning_result.get('imputed_columns') or cleaning_result.get('skipped_columns'):
        lines.append("\n## Cleaning Applied")
        if cleaning_result.get('imputed_columns'):
            method = cleaning_result['method_used'].replace('_', '-')
            # Format method name (knn -> k-NN, random-forest -> Random-Forest, etc.)
            if method == 'knn':
                method = 'k-NN'
            else:
                method = method.upper()
            cols = ', '.join(cleaning_result['imputed_columns'][:3])
            lines.append(f"- {method} imputation: {cols}")
        if cleaning_result.get('skipped_columns'):
            skipped = ', '.join(cleaning_result['skipped_columns'][:3])
            lines.append(f"- Skipped (too sparse): {skipped}")

    # Key Statistics (top 3-5)
    if analysis.get('statistics'):
        lines.append("\n## Key Statistics")
        for col, stats in list(analysis['statistics'].items())[:3]:
            lines.append(f"- **{col}**: mean={stats['mean']}, std={stats['std']}")

    # Insights
    if analysis.get('correlations'):
        lines.append("\n## Insights")
        # Find strongest correlation
        corr_dict = analysis['correlations']
        max_corr = 0
        max_pair = None
        for col1, corr_row in corr_dict.items():
            for col2, corr_val in corr_row.items():
                if col1 != col2 and abs(corr_val) > abs(max_corr):
                    max_corr = corr_val
                    max_pair = (col1, col2)
        if max_pair and abs(max_corr) > 0.7:
            lines.append(f"- Strong correlation ({max_corr:.2f}) between {max_pair[0]} & {max_pair[1]}")

    return '\n'.join(lines)


def generate_detailed_report(file_name: str,
                            profile: Dict[str, Any],
                            cleaning_result: Dict[str, Any],
                            outlier_result: Dict[str, Any],
                            analysis: Dict[str, Any],
                            viz_paths: List[str]) -> Dict[str, Any]:
    """
    Generate detailed markdown report file.

    Args:
        file_name: Original file name
        profile: Profiling results
        cleaning_result: Cleaning results
        outlier_result: Outlier detection results
        analysis: Analysis results
        viz_paths: List of visualization file paths

    Returns:
        Dictionary with report_path
    """
    timestamp = datetime.now().strftime('%Y-%m-%d')
    report_name = f"data_analysis_report_{timestamp}_{Path(file_name).stem}.md"
    reports_dir = Path.cwd() / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / report_name

    lines = []

    # Header
    lines.append(f"# Data Analysis Report: {file_name}")
    lines.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n---\n")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append(f"\nAnalyzed {profile['rows']:,} rows and {profile['cols']} columns.")
    if profile['missing']:
        lines.append(f"Found missing values in {len(profile['missing'])} columns.")
    if outlier_result['outlier_count'] > 0:
        lines.append(f"Detected {outlier_result['outlier_count']} outliers using {outlier_result['method_used']}.")

    # Data Quality Assessment
    lines.append("\n## Data Quality Assessment")
    lines.append(f"\n### Missing Values")
    if profile['missing']:
        for col, pct in profile['missing'].items():
            lines.append(f"- **{col}**: {pct}% missing")
    else:
        lines.append("- No missing values detected")

    lines.append(f"\n### Outliers")
    if outlier_result['outlier_count'] > 0:
        lines.append(f"- Method: {outlier_result['method_used']}")
        lines.append(f"- Count: {outlier_result['outlier_count']}")
    else:
        lines.append("- No outliers detected")

    # Cleaning Methods
    if cleaning_result.get('imputed_columns') or cleaning_result.get('skipped_columns'):
        lines.append("\n## Cleaning Applied")
        if cleaning_result.get('imputed_columns'):
            lines.append(f"\n### Imputation")
            lines.append(f"- Method: {cleaning_result['method_used']}")
            lines.append(f"- Columns: {', '.join(cleaning_result['imputed_columns'])}")
        if cleaning_result.get('skipped_columns'):
            lines.append(f"\n### Skipped Columns (Exceeds Threshold)")
            lines.append(f"- Columns: {', '.join(cleaning_result['skipped_columns'])}")
            lines.append(f"- Reason: Missing percentage exceeds imputation threshold")

    # Statistical Summary
    lines.append("\n## Statistical Summary")
    for col, stats in analysis.get('statistics', {}).items():
        lines.append(f"\n### {col}")
        lines.append(f"- Mean: {stats['mean']}")
        lines.append(f"- Std Dev: {stats['std']}")
        lines.append(f"- Min: {stats['min']}")
        lines.append(f"- Max: {stats['max']}")
        lines.append(f"- Median: {stats['median']}")

    # Visualizations
    if viz_paths:
        lines.append("\n## Visualizations")
        for viz_path in viz_paths:
            lines.append(f"\n![{Path(viz_path).stem}]({viz_path})")

    # Recommendations
    lines.append("\n## Recommendations")

    # Imputation recommendations based on missing data severity
    if profile['missing']:
        max_missing = max(profile['missing'].values())
        method_used = cleaning_result.get('method_used', 'unknown')

        if max_missing >= 30:
            lines.append(f"- **CRITICAL**: {max_missing}% missing exceeds reliability threshold (30%)")
            lines.append("  - Consider dropping columns with >30% missing")
            lines.append("  - If retaining: collect more data or use domain knowledge for imputation")
        elif max_missing >= 15:
            lines.append(f"- **Missing data**: {max_missing}% requires robust imputation")
            if method_used == 'simple':
                lines.append("  - Simple median/mode imputation may distort relationships")
                lines.append("  - **Recommended**: Random Forest imputation (15-30% range)")
                lines.append("  - Rerun with `--ml` flag for ML-based imputation")
        elif max_missing >= 5:
            lines.append(f"- **Missing data**: {max_missing}% warrants careful handling")
            if method_used == 'simple':
                lines.append("  - Consider k-NN imputation to preserve local structure")
                lines.append("  - Rerun with `--ml` flag for adaptive imputation")
        else:
            lines.append(f"- Missing data ({max_missing}%) is minimal - simple imputation is appropriate")

    if outlier_result['outlier_count'] > profile['rows'] * 0.1:
        lines.append("- **High outlier rate** (>10% of data) - verify data quality or adjust detection threshold")

    # Footer
    lines.append("\n---")
    lines.append("\n*Report generated by Advanced Data Analyzer*")

    report_path.write_text('\n'.join(lines))

    return {'report_path': str(report_path)}
