
import pandas as pd
import numpy as np
import os

class MRDataCleaner:
    def __init__(self, men_file_path, district_file_path):
        self.men_file_path = men_file_path
        self.district_file_path = district_file_path
        self.df = None

    def load_data(self):
        """Loads and merges the men's and district data."""
        df_men = pd.read_stata(self.men_file_path, convert_categoricals=False)
        
        if os.path.exists(self.district_file_path):
            df_district = pd.read_csv(self.district_file_path)
            # Prepare district data for merge
            df_district_subset = df_district[['dhsclust', 'pulse_adm2_en', 'pulse_study']].copy()
            df_district_subset.rename(columns={'dhsclust': 'cluster_number_dist', 'pulse_adm2_en': 'district_temp'}, inplace=True)
            # Merge the dataframes
            self.df = pd.merge(df_men, df_district_subset, left_on='mv001', right_on='cluster_number_dist', how='left')
        else:
            print(f"Warning: District file not found at {self.district_file_path}")
            self.df = df_men.assign(district_temp=np.nan, pulse_study=np.nan)

    def clean_data(self):
        """Applies cleaning logic to the DataFrame."""
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        new_cols = {
            'wt': self.df['mv005'] / 1000000,
            'cluster_number': self.df['mv001'],
            'region': self.df['mv024'],
            'district': self.df['district_temp'].astype('category').cat.codes
        }

        new_cols.update(self._create_literacy_variables())
        new_cols.update(self._create_employment_variables())

        self.df = self.df.assign(**new_cols)

    def _create_literacy_variables(self):
        """Creates variables related to literacy."""
        recode_map = {2: 1, 1: 2, 0: 3, 3: 4, 4: 5}
        rc_litr_cats = self.df['mv155'].map(recode_map)
        rc_litr_cats.loc[self.df['mv106'] == 3] = 0

        liter_dummies = {
            'liter_higher_sec': 1,
            'liter_whole_sentence': 2,
            'liter_part_sentence': 3,
            'liter_cannot_read': 4,
            'liter_no_card': 5,
        }
        new_cols = {'rc_litr_cats': rc_litr_cats}
        for var_name, code in liter_dummies.items():
            new_cols[var_name] = np.where(rc_litr_cats == code, 1, 0)
        
        new_cols['liter_blind'] = np.where(rc_litr_cats == 0, 1, 0)

        rc_litr = pd.Series(0, index=self.df.index)
        rc_litr.loc[(self.df['mv106'] == 3) | (self.df['mv155'] == 1) | (self.df['mv155'] == 2)] = 1
        new_cols['rc_litr'] = rc_litr
        
        return new_cols

    def _create_employment_variables(self):
        """Creates variables related to employment and occupation."""
        empl_recode = {0: 0, 1: 1, 2: 2, 3: 2, 8: 9}
        rc_empl = self.df['mv731'].map(empl_recode)

        occup_recode = {0: 1, 4: 2, 5: 2, 3: 3, 9: 4, 1: 5, 2: 5, 6: 5, 7: 5, 8: 5, 10: 5, 96: 5}
        man_occup = self.df['mv717'].map(occup_recode)

        new_cols = {
            'rc_empl': rc_empl,
            'man_occup': man_occup
        }

        occup_dummies = {'not_work': 1, 'agric': 2, 'sales': 3, 'unskill': 4, 'other': 5}
        for var_name, code in occup_dummies.items():
            col_name = f'mn_occup_{var_name}'
            new_col = pd.Series(np.where(man_occup == code, 1, 0), index=self.df.index)
            new_col.loc[man_occup.isnull()] = np.nan
            new_cols[col_name] = new_col

        rc_empl_type = self.df['mv719'].copy()
        rc_empl_type.loc[~self.df['mv731'].isin([1, 2, 3])] = np.nan
        new_cols['rc_empl_type'] = rc_empl_type
        
        return new_cols

    def keep_variables(self):
        """Keeps only the specified variables."""
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        columns_to_keep = [
            'mv106', 'mv155', 'mv731', 'mv717', 'mv170', 'wt', 'cluster_number', 'region', 'district_temp', 'pulse_study',
            'rc_litr_cats', 'liter_higher_sec', 'liter_whole_sentence', 'liter_part_sentence', 'liter_cannot_read',
            'liter_no_card', 'liter_blind', 'rc_litr', 'rc_empl', 'man_occup', 'mn_occup_not_work', 'mn_occup_agric',
            'mn_occup_sales', 'mn_occup_unskill', 'mn_occup_other', 'rc_empl_type'
        ]
        
        # Ensure all columns to keep exist, adding any that are missing
        for col in columns_to_keep:
            if col not in self.df.columns:
                self.df[col] = np.nan
        
        self.df = self.df[columns_to_keep]

    def save_data(self, output_path_csv):
        """Saves the cleaned DataFrame to a CSV file."""
        if self.df is None:
            raise ValueError("No data to save.")

        self.df.to_csv(output_path_csv, index=False)

if __name__ == '__main__':
    # Define file paths
    men_data_path = '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/raw/MDMR81FL.DTA'
    district_data_path = '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/raw/MDGE81FL_DISTRICT.csv'
    cleaned_data_path_csv = '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/cleaned/mrdata_clean.csv'
    
    # Instantiate the cleaner
    mr_cleaner = MRDataCleaner(men_data_path, district_data_path)
    
    # Load and merge data
    mr_cleaner.load_data()
    
    # Clean the data
    mr_cleaner.clean_data()
    
    # Keep only necessary variables
    mr_cleaner.keep_variables()
    
    # Save the cleaned data
    mr_cleaner.save_data(cleaned_data_path_csv)
    
    print(f"Cleaned data saved to {cleaned_data_path_csv}")
