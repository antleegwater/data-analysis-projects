# To Do

## Current Status:
- All data cleaning scripts (`HR_Data_Cleaning.py`, `ir_data_cleaning.py`, `mr_data_cleaning.py`, and `pr_data_cleaning.py`) have been successfully refactored to improve performance and handle missing data. They are all running without errors.
- Jupyter has been installed in the virtual environment.

## Next Steps:
1. Convert the analysis notebooks to Python scripts, starting with `child_diet_analysis.ipynb`.
2. Run the converted Python scripts to verify the analysis.

---

# Proposed Python Conversion Plan

The goal is to create a unified, end-to-end Python pipeline that is modular, easy to run, and maintainable.

**1. Convert Stata Scripts to Python Modules:**

*   **Data Cleaning:**
    *   I will analyze the remaining Stata data cleaning files (`IR DATA Cleaning.do`, `MR Data Cleaning.do`, `PR Data Cleaning.do`) and convert them into Python scripts.
    *   I will follow the object-oriented structure used in `HR_Data_Cleaning.py` and `KR_Data_Cleaning.py` by creating a dedicated class for each cleaning script (e.g., `IRDataCleaner`, `MRDataCleaner`, `PRDataCleaner`).
*   **Data Analysis:**
    *   I will convert the Stata analysis files (`Child Diet Analysis.do`, `Child Stunting Analysis.do`, `Household Analysis.do`, `RQ3.do`) into Python scripts or Jupyter notebooks.
    *   This will involve using `pandas` for data manipulation and aggregation, and libraries like `statsmodels` for statistical analysis to replicate the Stata output.

**2. Create a Master Control Script:**

*   I will create a `main.py` script that serves as the master control file, equivalent to the `Master.do` file.
*   This script will import and run the data cleaning and analysis modules in the correct order.
*   It will handle file paths and dependencies, making the project easy to execute with a single command (e.g., `python main.py`).

**3. Standardize Data Formats:**

*   While the current Python scripts save cleaned data back to Stata `.dta` format, I recommend switching to a more Python-native format like CSV or Parquet for intermediate and final datasets. This will improve compatibility with Python libraries and avoid potential issues with Stata file formats.

**4. Project Structure:**

I suggest the following project structure for better organization:

```
/MadagAnalysis/
|-- data/
|   |-- raw/
|   |   |-- MDHR81FL.DTA
|   |   |-- MDKR81FL.DTA
|   |   |-- ...
|   |-- cleaned/
|       |-- hr_data_clean.csv
|       |-- kr_data_clean.csv
|       |-- ...
|-- notebooks/
|   |-- RQ4.ipynb
|   |-- exploratory_analysis.ipynb
|-- src/
|   |-- __init__.py
|   |-- cleaning/
|   |   |-- __init__.py
|   |   |-- hr_cleaning.py
|   |   |-- kr_cleaning.py
|   |   |-- ir_cleaning.py
|   |   |-- mr_cleaning.py
|   |   |-- pr_cleaning.py
|   |-- analysis/
|   |   |-- __init__.py
|   |   |-- child_diet_analysis.py
|   |   |-- child_stunting_analysis.py
|   |   |-- ...
|   |-- main.py
|-- requirements.txt
|-- README.md
```