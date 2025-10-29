

import pandas as pd
import os

class ChildAnalysisMerger:
    def __init__(self, clean_data_path):
        self.clean_data_path = clean_data_path
        self.hr_df = None
        self.pr_df = None
        self.kr_df = None

    def load_data(self):
        """Loads the cleaned CSV files into pandas DataFrames."""
        self.hr_df = pd.read_csv(os.path.join(self.clean_data_path, 'hrdata_clean.csv'))
        self.pr_df = pd.read_csv(os.path.join(self.clean_data_path, 'prdata_clean.csv'))
        self.kr_df = pd.read_csv(os.path.join(self.clean_data_path, 'krdata_clean.csv'))

    def create_stunting_analysis_data(self, output_path_csv):
        """Creates and saves the child stunting analysis dataset."""
        if self.hr_df is None or self.pr_df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        # Prepare HR data
        hr_temp = self.hr_df.copy()
        hr_temp.rename(columns={'hv001': 'cluster_line', 'hv002': 'hh_line'}, inplace=True)

        # Prepare PR data
        pr_temp = self.pr_df.copy()
        pr_temp.rename(columns={'hv001': 'cluster_line', 'hv002': 'hh_line'}, inplace=True)
        pr_temp = pr_temp[pr_temp['hc1'] < 60]
        columns_to_keep = [
            'cluster_line', 'hh_line', 'nt_ch_stunt', 'nt_ch_sev_stunt', 'nt_ch_mean_haz',
            'nt_ch_wast', 'nt_ch_sev_wast', 'nt_ch_underwt', 'nt_ch_sev_underwt'
        ]
        pr_temp = pr_temp[columns_to_keep]

        # Merge dataframes
        merged_df = pd.merge(pr_temp, hr_temp, on=['cluster_line', 'hh_line'], how='inner')

        # Save the merged dataframe
        merged_df.to_csv(output_path_csv, index=False)
        print(f"Child stunting analysis data saved to {output_path_csv}")

    def create_diet_analysis_data(self, output_path_csv):
        """Creates and saves the child diet analysis dataset."""
        if self.hr_df is None or self.kr_df is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        # Prepare HR data
        hr_temp = self.hr_df.copy()
        hr_temp.rename(columns={'hv001': 'cluster_line', 'hv002': 'hh_line'}, inplace=True)

        # Prepare KR data
        kr_temp = self.kr_df.copy()
        kr_temp.rename(columns={'v001': 'cluster_line', 'v002': 'hh_line'}, inplace=True)

        # Merge dataframes
        merged_df = pd.merge(kr_temp, hr_temp, on=['cluster_line', 'hh_line'], how='inner')

        # Save the merged dataframe
        merged_df.to_csv(output_path_csv, index=False)
        print(f"Child diet analysis data saved to {output_path_csv}")

if __name__ == '__main__':
    # This assumes the script is run from a directory where 'data/cleaned' is accessible.
    cleaned_data_directory = 'data/cleaned'
    
    # Instantiate the merger
    merger = ChildAnalysisMerger(cleaned_data_directory)
    
    # Load the cleaned datasets
    merger.load_data()
    
    # Define output paths
    stunting_output_path_csv = os.path.join(cleaned_data_directory, 'child_stunting_analysis.csv')
    diet_output_path_csv = os.path.join(cleaned_data_directory, 'child_diet_analysis.csv')
    
    # Create and save the stunting analysis data
    merger.create_stunting_analysis_data(stunting_output_path_csv)
    
    # Create and save the diet analysis data
    merger.create_diet_analysis_data(diet_output_path_csv)
