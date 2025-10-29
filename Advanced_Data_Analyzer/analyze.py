"""Main pipeline orchestrator for Advanced Data Analyzer."""
from pathlib import Path
from typing import Dict, Any, Optional

from analyzer.ingestion import ingest_file
from analyzer.profiling import profile_data
from analyzer.cleaning import impute_missing, detect_outliers
from analyzer.analysis import analyze_data
from analyzer.visualization import generate_visualizations
from analyzer.reporting import generate_chat_report, generate_detailed_report


def analyze_file(file_path: str, apply_ml_cleaning: bool = False,
                 impute_threshold: float = 30.0) -> Dict[str, Any]:
    """
    Run complete analysis pipeline on a data file.

    Args:
        file_path: Path to input file (CSV, JSON, Excel, Parquet)
        apply_ml_cleaning: If True, apply ML-based imputation/outlier detection
        impute_threshold: Maximum missing percentage to impute (default: 30.0)

    Returns:
        Dictionary with:
            - chat_report: Compact markdown report string
            - detailed_report_path: Path to detailed markdown file
            - visualizations: List of visualization paths
            - refinement_options: Suggested ML methods (if not applied)
    """
    print(f"Starting analysis of {Path(file_path).name}...")

    # Phase 1: Ingestion
    print("1/6 Ingesting file...")
    ingestion_result = ingest_file(file_path)
    current_file = ingestion_result['file_path']

    # Phase 2: Profiling
    print("2/6 Profiling data...")
    profile = profile_data(current_file)

    # Phase 3: Cleaning
    print("3/6 Cleaning data...")
    cleaning_result = {'imputed_columns': [], 'method_used': 'none'}
    outlier_result = {'outlier_count': 0, 'method_used': 'none'}

    if apply_ml_cleaning:
        # Apply ML-based cleaning
        if profile['missing']:
            clean_result = impute_missing(current_file, profile, method='auto',
                                         impute_threshold=impute_threshold)
            current_file = clean_result['file_path']
            cleaning_result = clean_result

        if profile['numeric_cols']:
            outlier_result = detect_outliers(current_file, profile, method='auto')
    else:
        # Basic cleaning only
        if profile['missing']:
            clean_result = impute_missing(current_file, profile, method='simple',
                                         impute_threshold=impute_threshold)
            current_file = clean_result['file_path']
            cleaning_result = clean_result

    # Phase 4: Analysis
    print("4/6 Analyzing data...")
    analysis = analyze_data(current_file, profile)

    # Phase 5: Visualization
    print("5/6 Generating visualizations...")
    viz_result = generate_visualizations(current_file, profile, analysis)

    # Phase 6: Reporting
    print("6/6 Generating reports...")
    chat_report = generate_chat_report(profile, cleaning_result, outlier_result, analysis)
    detailed_result = generate_detailed_report(
        file_name=Path(file_path).name,
        profile=profile,
        cleaning_result=cleaning_result,
        outlier_result=outlier_result,
        analysis=analysis,
        viz_paths=viz_result['visualizations']
    )

    result = {
        'chat_report': chat_report,
        'detailed_report_path': detailed_result['report_path'],
        'visualizations': viz_result['visualizations']
    }

    # Add refinement suggestions if ML not applied
    if not apply_ml_cleaning:
        suggestions = []
        if profile['missing']:
            max_missing = max(profile['missing'].values())
            if max_missing >= 30:
                suggestions.append(f"⚠️ CRITICAL: {max_missing:.1f}% missing - consider dropping columns or collecting more data")
            elif max_missing >= 15:
                suggestions.append(f"Apply Random Forest imputation ({max_missing:.1f}% missing - preserves non-linear relationships)")
            elif max_missing >= 5:
                suggestions.append(f"Apply k-NN imputation ({max_missing:.1f}% missing - preserves local structure)")
        if len(profile['numeric_cols']) >= 5:
            suggestions.append("Run Isolation Forest outlier detection (high-dimensional data - catches complex anomalies)")

        result['refinement_options'] = suggestions

    print("Analysis complete!")
    return result


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Advanced Data Analyzer')
    parser.add_argument('file_path', help='Path to data file (CSV, JSON, Excel, Parquet)')
    parser.add_argument('--ml', action='store_true', help='Apply ML-based cleaning (auto-select imputation method)')
    parser.add_argument('--impute-threshold', type=float, default=30.0,
                       help='Maximum missing %% to impute (default: 30.0, columns above threshold kept as NaN)')

    args = parser.parse_args()

    result = analyze_file(args.file_path, apply_ml_cleaning=args.ml, impute_threshold=args.impute_threshold)

    print("\n" + "="*60)
    print(result['chat_report'])
    print("="*60)
    print(f"\nDetailed report: {result['detailed_report_path']}")
    print(f"Visualizations: {len(result['visualizations'])} generated")

    if result.get('refinement_options'):
        print("\nRefinement options available:")
        for option in result['refinement_options']:
            print(f"  - {option}")
        print("\nRun with --ml flag to apply ML-based cleaning")
