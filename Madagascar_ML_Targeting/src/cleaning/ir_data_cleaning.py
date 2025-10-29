
import pandas as pd
import numpy as np
import os

class IRDataCleaner:
    def __init__(self, ir_file_path, district_file_path):
        self.ir_file_path = ir_file_path
        self.district_file_path = district_file_path
        self.df = None

    def load_data(self):
        """Loads and merges the individual women's and district data."""
        df_ir = pd.read_stata(self.ir_file_path, convert_categoricals=False)
        
        if os.path.exists(self.district_file_path):
            df_district = pd.read_csv(self.district_file_path)
            df_district_subset = df_district[['dhsclust', 'pulse_adm2_en', 'pulse_study']].copy()
            df_district_subset.rename(columns={'dhsclust': 'cluster_number_dist', 'pulse_adm2_en': 'district_temp'}, inplace=True)
            self.df = pd.merge(df_ir, df_district_subset, left_on='v001', right_on='cluster_number_dist', how='left')
        else:
            print(f"Warning: District file not found at {self.district_file_path}")
            self.df = df_ir.assign(district_temp=np.nan, pulse_study=np.nan)

    def clean_data(self):
        """Applies cleaning logic to the DataFrame."""
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        new_cols = {
            'wt': self.df['v005'] / 1000000,
            'cluster_number': self.df['v001'],
            'region': self.df['v024'],
            'district': self.df['district_temp'].astype('category').cat.codes
        }

        new_cols.update(self._create_decision_making_variables())
        new_cols.update(self._create_family_planning_variables())
        new_cols.update(self._create_anc_variables())
        new_cols.update(self._create_occupation_variables())

        self.df = self.df.assign(**new_cols)

    def _create_decision_making_variables(self):
        """Creates variables related to women's decision-making."""
        we_decide_all = pd.Series(np.nan, index=self.df.index)
        condition = self.df['v502'] == 1
        we_decide_all.loc[condition] = (
            self.df.loc[condition, 'v743a'].isin([1, 2]) &
            self.df.loc[condition, 'v743b'].isin([1, 2]) &
            self.df.loc[condition, 'v743d'].isin([1, 2])
        ).astype(int)
        return {'we_decide_all': we_decide_all}

    def _create_family_planning_variables(self):
        """Creates variables related to family planning decisions."""
        fp_decyes_wmn = pd.Series(0, index=self.df.index)
        fp_decyes_wmn.loc[self.df['v632'].isnull()] = np.nan
        fp_decyes_wmn.loc[(self.df['v502'] != 1) | (self.df['v213'] != 0) | (self.df['v312'] == 0)] = np.nan
        fp_decyes_wmn.loc[self.df['v632'].isin([1, 3])] = 1

        fp_decno_wmn = pd.Series(0, index=self.df.index)
        fp_decno_wmn.loc[self.df['v632a'].isnull()] = np.nan
        fp_decno_wmn.loc[(self.df['v502'] != 1) | (self.df['v213'] != 0) | (self.df['v312'] != 0)] = np.nan
        fp_decno_wmn.loc[self.df['v632a'].isin([1, 3])] = 1

        fp_decno_nonuser = self.df['v632a'].copy()
        fp_decno_nonuser.loc[(self.df['v502'] != 1) | (self.df['v213'] != 0) | (self.df['v312'] != 0)] = np.nan
        
        return {
            'fp_decyes_wmn': fp_decyes_wmn,
            'fp_decno_wmn': fp_decno_wmn,
            'fp_decno_nonuser': fp_decno_nonuser
        }

    def _create_anc_variables(self):
        """Creates variables related to Antenatal Care (ANC)."""
        period = 60
        age = self.df['b19_01']

        conditions = [
            age >= period,
            self.df['m2a_1'] == 9,
            self.df['m2a_1'] == 1,
            (self.df['m2b_1'] == 1) | (self.df['m2c_1'] == 1),
            (self.df['m2d_1'] == 1) | (self.df['m2e_1'] == 1),
            (self.df['m2f_1'] == 1) | (self.df['m2g_1'] == 1) | (self.df['m2h_1'] == 1) | (self.df['m2i_1'] == 1) | (self.df['m2j_1'] == 1) | (self.df['m2k_1'] == 1) | (self.df['m2l_1'] == 1) | (self.df['m2m_1'] == 1),
            self.df['m2a_1'].notna()
        ]
        choices = [np.nan, 9, 1, 2, 3, 4, 6]
        rh_anc_pv = pd.Series(np.select(conditions, choices, default=np.nan), index=self.df.index)

        anc_pvskill = pd.Series(np.nan, index=self.df.index)
        anc_pvskill.loc[rh_anc_pv.isin([1, 2])] = 1
        anc_pvskill.loc[rh_anc_pv.isin([3, 4, 5, 6, 7, 8, 9])] = 0
        anc_pvskill.loc[age >= period] = np.nan

        return {
            'age': age,
            'rh_anc_pv': rh_anc_pv,
            'anc_pvskill': anc_pvskill
        }

    def _create_occupation_variables(self):
        """Creates variables related to women's occupation."""
        recode_map = {0: 1, 4: 2, 5: 2, 3: 3, 9: 4, 1: 5, 2: 5, 6: 5, 7: 5, 8: 5, 10: 5, 96: 5}
        woman_occup = self.df['v717'].map(recode_map)

        occup_dummies = {'not_work': 1, 'agric': 2, 'sales': 3, 'unskill': 4, 'other': 5}
        new_cols = {'woman_occup': woman_occup}
        for var_name, code in occup_dummies.items():
            col_name = f'wmn_occup_{var_name}'
            new_col = pd.Series(np.where(woman_occup == code, 1, 0), index=self.df.index)
            new_col.loc[woman_occup.isnull()] = np.nan
            new_cols[col_name] = new_col
            
        return new_cols

    def keep_variables(self):
        """Keeps only the specified variables."""
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        columns_to_keep = [
            'v208', 'v213', 'b19_01', 'v438', 'v445', 'v106', 'v155', 'v731', 'v717', 'v170', 'wt',
            'cluster_number', 'region', 'district_temp', 'pulse_study', 'we_decide_all', 'fp_decyes_wmn',
            'fp_decno_wmn', 'rh_anc_pv', 'anc_pvskill', 'fp_decno_nonuser', 'woman_occup'
        ]
        wmn_occup_cols = [col for col in self.df.columns if col.startswith('wmn_occup_')]
        columns_to_keep.extend(wmn_occup_cols)
        columns_to_keep = list(dict.fromkeys(columns_to_keep)) # remove duplicates

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
    ir_cleaner = IRDataCleaner(
        '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/raw/MDIR81FL.DTA',
        '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/raw/MDGE81FL_DISTRICT.csv'
    )
    ir_cleaner.load_data()
    ir_cleaner.clean_data()
    ir_cleaner.keep_variables()
    ir_cleaner.save_data('/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/cleaned/irdata_clean.csv')
    print(f"Cleaned data saved to /mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/cleaned/irdata_clean.csv")
