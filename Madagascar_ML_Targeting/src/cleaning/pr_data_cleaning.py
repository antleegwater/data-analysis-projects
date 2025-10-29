import pandas as pd
import numpy as np

class PRDataCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        """Loads the Stata file into a pandas DataFrame."""
        self.df = pd.read_stata(self.file_path)

    def clean_data(self):
        """Applies cleaning logic to the DataFrame."""
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        self.df['hc70'] = pd.to_numeric(self.df['hc70'], errors='coerce')
        self.df['hc71'] = pd.to_numeric(self.df['hc71'], errors='coerce')
        self.df['hc72'] = pd.to_numeric(self.df['hc72'], errors='coerce')

        new_cols = {'wt': self.df['hv005'] / 1000000}

        new_cols.update(self._create_stunting_variables(new_cols['wt']))
        new_cols.update(self._create_wasting_variables(new_cols['wt']))
        new_cols.update(self._create_underweight_variables(new_cols['wt']))
        
        self.df = self.df.assign(**new_cols)

    def _create_stunting_variables(self, weights):
        """Creates variables related to stunting."""
        new_cols = {}
        
        # Severely stunted
        nt_ch_sev_stunt = pd.Series(0, index=self.df.index)
        nt_ch_sev_stunt.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_sev_stunt.loc[self.df['hc70'] >= 9996] = np.nan
        nt_ch_sev_stunt.loc[(self.df['hc70'] < -300) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_sev_stunt'] = nt_ch_sev_stunt

        # Stunted
        nt_ch_stunt = pd.Series(0, index=self.df.index)
        nt_ch_stunt.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_stunt.loc[self.df['hc70'] >= 9996] = np.nan
        nt_ch_stunt.loc[(self.df['hc70'] < -200) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_stunt'] = nt_ch_stunt

        # Mean haz
        haz = self.df['hc70'] / 100
        haz.loc[self.df['hc70'] >= 9996] = np.nan
        new_cols['haz'] = haz
        
        child_under_5 = self.df['hv103'] == 1
        haz_values = haz[child_under_5].dropna()
        
        if not haz_values.empty:
            mean_haz = np.average(haz_values, weights=weights[haz_values.index])
            new_cols['nt_ch_mean_haz'] = round(mean_haz, 1)
        else:
            new_cols['nt_ch_mean_haz'] = np.nan
            
        return new_cols

    def _create_wasting_variables(self, weights):
        """Creates variables related to wasting."""
        new_cols = {}
        
        # Severely wasted
        nt_ch_sev_wast = pd.Series(0, index=self.df.index)
        nt_ch_sev_wast.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_sev_wast.loc[self.df['hc72'] >= 9996] = np.nan
        nt_ch_sev_wast.loc[(self.df['hc72'] < -300) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_sev_wast'] = nt_ch_sev_wast

        # Wasted
        nt_ch_wast = pd.Series(0, index=self.df.index)
        nt_ch_wast.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_wast.loc[self.df['hc72'] >= 9996] = np.nan
        nt_ch_wast.loc[(self.df['hc72'] < -200) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_wast'] = nt_ch_wast

        # Overweight for height
        nt_ch_ovwt_ht = pd.Series(0, index=self.df.index)
        nt_ch_ovwt_ht.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_ovwt_ht.loc[self.df['hc72'] >= 9996] = np.nan
        nt_ch_ovwt_ht.loc[(self.df['hc72'] > 200) & (self.df['hc72'] < 9996) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_ovwt_ht'] = nt_ch_ovwt_ht

        # Mean whz
        whz = self.df['hc72'] / 100
        whz.loc[self.df['hc72'] >= 9996] = np.nan
        new_cols['whz'] = whz
        
        child_under_5 = self.df['hv103'] == 1
        whz_values = whz[child_under_5].dropna()

        if not whz_values.empty:
            mean_whz = np.average(whz_values, weights=weights[whz_values.index])
            new_cols['nt_ch_mean_whz'] = round(mean_whz, 1)
        else:
            new_cols['nt_ch_mean_whz'] = np.nan
            
        return new_cols

    def _create_underweight_variables(self, weights):
        """Creates variables related to being underweight."""
        new_cols = {}
        
        # Severely underweight
        nt_ch_sev_underwt = pd.Series(0, index=self.df.index)
        nt_ch_sev_underwt.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_sev_underwt.loc[self.df['hc71'] >= 9996] = np.nan
        nt_ch_sev_underwt.loc[(self.df['hc71'] < -300) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_sev_underwt'] = nt_ch_sev_underwt

        # Underweight
        nt_ch_underwt = pd.Series(0, index=self.df.index)
        nt_ch_underwt.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_underwt.loc[self.df['hc71'] >= 9996] = np.nan
        nt_ch_underwt.loc[(self.df['hc71'] < -200) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_underwt'] = nt_ch_underwt

        # Overweight for age
        nt_ch_ovwt_age = pd.Series(0, index=self.df.index)
        nt_ch_ovwt_age.loc[self.df['hv103'] != 1] = np.nan
        nt_ch_ovwt_age.loc[self.df['hc71'] >= 9996] = np.nan
        nt_ch_ovwt_age.loc[(self.df['hc71'] > 200) & (self.df['hc71'] < 9996) & (self.df['hv103'] == 1)] = 1
        new_cols['nt_ch_ovwt_age'] = nt_ch_ovwt_age

        # Mean waz
        waz = self.df['hc71'] / 100
        waz.loc[self.df['hc71'] >= 9996] = np.nan
        new_cols['waz'] = waz

        child_under_5 = self.df['hv103'] == 1
        waz_values = waz[child_under_5].dropna()

        if not waz_values.empty:
            mean_waz = np.average(waz_values, weights=weights[waz_values.index])
            new_cols['nt_ch_mean_waz'] = round(mean_waz, 1)
        else:
            new_cols['nt_ch_mean_waz'] = np.nan
            
        return new_cols

    def keep_variables(self):
        """Keeps only the specified variables."""
        if self.df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        columns_to_keep = [
            'hv001', 'hv002', 'hc1', 'hc70', 'hc71', 'hc72', 'hv103', 'wt',
            'nt_ch_sev_stunt', 'nt_ch_stunt', 'haz', 'nt_ch_mean_haz',
            'nt_ch_sev_wast', 'nt_ch_wast', 'nt_ch_ovwt_ht', 'whz', 'nt_ch_mean_whz',
            'nt_ch_sev_underwt', 'nt_ch_underwt', 'nt_ch_ovwt_age', 'waz', 'nt_ch_mean_waz'
        ]
        
        # Ensure all columns to keep exist in the DataFrame, add them with NaN if they don't
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
    raw_data_path = '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/raw/MDPR81FL.DTA'
    cleaned_data_path_csv = '/mnt/c/Users/hp800/WSLWorkspace/MiniProjects/MadagAnalysis/PythonConversion/data/cleaned/prdata_clean.csv'
    
    # Instantiate the cleaner
    pr_cleaner = PRDataCleaner(raw_data_path)
    
    # Load the data
    pr_cleaner.load_data()
    
    # Clean the data
    pr_cleaner.clean_data()
    
    # Keep only necessary variables
    pr_cleaner.keep_variables()
    
    # Save the cleaned data
    pr_cleaner.save_data(cleaned_data_path_csv)
    
    print(f"Cleaned data saved to {cleaned_data_path_csv}")
