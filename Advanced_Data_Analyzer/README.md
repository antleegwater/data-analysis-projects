# Advanced Data Analyzer - Claude Skill

Intelligent data analysis skill for Claude Code with ML-based cleaning, multi-format support, and token-efficient processing.

## Features

### Multi-Format Support
- CSV (existing standard)
- JSON (nested structures flattened)
- Excel (.xlsx, first data sheet)
- Parquet (efficient for large files)

### Intelligent Data Cleaning
- **Progressive Imputation**:
  - <5% missing: Median/mode
  - 5-15% missing: k-NN imputation
  - 15-30% missing: Random Forest imputation
- **Adaptive Outlier Detection**:
  - Low-dimensional: IQR method
  - Mid-dimensional: k-NN distance
  - High-dimensional: Isolation Forest

### Token-Efficient Architecture
- Intermediate results stored as Parquet files
- Only metadata and summaries in context
- Handles 1M+ row datasets without overflow

### Hybrid Workflow
1. **Auto-run**: Fast basic analysis with simple cleaning
2. **Refinement**: Suggest ML methods based on findings

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Usage

### As Claude Skill
Upload or reference data file in Claude Code. Skill activates automatically.

### Command Line
```bash
# Basic analysis
python analyze.py data.csv

# With ML cleaning
python analyze.py data.csv --ml

# JSON file
python analyze.py api_data.json --ml
```

## Architecture

```
File → Ingestion → Profiling → Cleaning → Analysis → Visualization → Reporting
         ↓            ↓           ↓           ↓            ↓             ↓
      parquet      metadata    parquet    metadata     PNGs     MD report
```

Each stage:
- Writes intermediate Parquet to `/tmp/`
- Passes metadata dict (not raw data)
- Token-efficient execution

## Output

### Chat Report (~500-800 tokens)
Compact markdown with:
- Data overview
- Data quality summary
- Cleaning applied
- Key statistics
- Top insights

### Detailed Report (markdown file)
Comprehensive analysis including:
- Executive summary
- Full data quality assessment
- Complete statistical tables
- Methodology explanations
- Embedded visualizations
- Recommendations

Optional Word (.docx) export via `document-skills` or `pandoc`.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_cleaning.py -v

# Test with coverage
pytest tests/ --cov=analyzer
```

## Design Principles

1. **DRY**: Modular pipeline stages
2. **YAGNI**: MVP excludes SPSS/SAS (Phase 2)
3. **TDD**: Comprehensive test coverage
4. **Token Efficiency**: File-based communication
5. **Progressive Enhancement**: Basic → ML cleaning

## Future Enhancements (Phase 2)

- SAS/SPSS support with metadata preservation
- FHIR-specific JSON parsing
- Delta Lake versioning
- Custom pipeline configuration
- Advanced feature engineering (Box-Cox, k-means binning)

## References

- Design: `/docs/plans/2025-10-27-advanced-data-analyzer-design.md`
- Implementation: This plan
- Base: [CSV Data Summarizer](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill)
