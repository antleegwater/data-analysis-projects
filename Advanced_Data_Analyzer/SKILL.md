---
name: advanced-data-analyzer
description: Analyzes CSV, JSON, Excel, and Parquet files with ML-based cleaning, generates summary stats, and creates visualizations using intelligent imputation and outlier detection.
metadata:
  version: 1.0.0
  dependencies: python>=3.8, pandas>=2.0.0, scikit-learn>=1.3.0, matplotlib>=3.7.0, seaborn>=0.12.0, pyarrow>=10.0.0, openpyxl>=3.0.0
---

# Advanced Data Analyzer

This Skill analyzes tabular data files with intelligent data cleaning and provides comprehensive reports with statistical insights and visualizations.

## When to Use This Skill

Claude should use this Skill whenever the user:
- Uploads or references CSV, JSON, Excel, or Parquet files
- Asks to summarize, analyze, or visualize tabular data
- Requests data quality assessment or cleaning
- Wants to understand data structure with advanced methods
- Needs missing value imputation or outlier detection

## How It Works

## ⚠️ CRITICAL BEHAVIOR REQUIREMENT ⚠️

**IMMEDIATELY AND AUTOMATICALLY:**
1. Run the comprehensive analysis
2. Generate ALL relevant visualizations
3. Present complete results
4. If data quality issues detected, suggest ML refinement

**DO NOT ASK "What would you like me to do?"**

### Automatic Analysis Pipeline (6 Stages):

**The skill intelligently adapts to different data types and formats.**

1. **Ingestion** - Auto-detect format (CSV, JSON, Excel, Parquet) and load
2. **Profiling** - Identify missing values, column types, dimensionality
3. **Cleaning** - Apply appropriate imputation and outlier detection
   - **<5% missing**: Simple median/mode imputation
   - **5-15% missing**: k-NN imputation
   - **15-30% missing**: Random Forest imputation
   - **Low-dimensional (<5 cols)**: IQR outlier detection
   - **High-dimensional (≥10 cols)**: Isolation Forest outliers
4. **Analysis** - Generate descriptive statistics and correlations
5. **Visualization** - Create adaptive plots (heatmaps, distributions, etc.)
6. **Reporting** - Produce compact chat report + detailed markdown file

### Hybrid Workflow

**Phase 1 (Auto-run):**
- Basic cleaning with simple methods
- Fast initial analysis
- Present findings

**Phase 2 (Refinement Prompt):**
If significant data quality issues detected:
> "Refinement options available:
> - Apply k-NN imputation (12% missing in 'income')
> - Run Isolation Forest (10 numeric columns)
>
> Run advanced cleaning? (yes/no)"

### Usage

The Skill provides a Python function `analyze_file(file_path, apply_ml_cleaning)`:
- Accepts path to CSV, JSON, Excel, or Parquet file
- Returns compact chat report + detailed markdown report
- Generates visualizations automatically

### Example Prompts

> "Analyze this sales data CSV"

> "What insights can you find in customer_data.json?"

> "Check data quality in survey_results.xlsx"

### Example Output

**Chat Report (Compact):**

## Data Overview
- 50,000 rows × 12 columns

## Data Quality
- Missing: age (12%), income (8%), zip (3%)
- Outliers: 23 flagged (isolation_forest)

## Cleaning Applied
- K-NN imputation: age, income, zip

## Key Statistics
- **age**: mean=34.2, std=12.1
- **income**: mean=65000, std=15000

## Insights
- Strong correlation (0.85) between age & income

**Detailed Report:**
Saved to `/tmp/data_analysis_report_2025-10-27_sales_data.md`

Includes:
- Executive summary
- Complete data quality assessment
- Full statistical tables
- Methodology explanations
- All visualizations embedded
- Recommendations

### Optional Word Export

After generating markdown report:
> "Report saved to data_analysis_report.md. Convert to Word format? (yes/no)"

## Files

- `analyze.py` - Main pipeline orchestrator
- `analyzer/ingestion.py` - Multi-format file loading
- `analyzer/profiling.py` - Data quality profiling
- `analyzer/cleaning.py` - ML-based imputation and outlier detection
- `analyzer/analysis.py` - Statistical analysis
- `analyzer/visualization.py` - Adaptive chart generation
- `analyzer/reporting.py` - Report generation
- `requirements.txt` - Python dependencies
- `resources/` - Sample data files
- `tests/` - Comprehensive test suite

## Advanced Features

- **Token Efficiency**: Intermediate results stored as parquet files, only summaries in context
- **Format Detection**: Auto-identifies CSV, JSON (nested), Excel (multi-sheet), Parquet
- **Intelligent Cleaning**: Method selection based on data characteristics
- **Multivariate Outliers**: Catches complex anomalies univariate methods miss
- **Professional Reports**: Publication-ready markdown with optional Word export

## Notes

- Handles datasets up to 1M+ rows efficiently
- Nested JSON automatically flattened
- Excel uses first data sheet by default
- High-cardinality columns (>50 unique) excluded from visualizations
- All ML methods use scikit-learn for reliability
