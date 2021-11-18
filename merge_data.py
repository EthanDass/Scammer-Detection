import sys
import os
import pandas as pd

# This script combines data files into single datafiles

# Returns the file name without scammer label or extensions
def get_file_prefix(file_name):
  return file_name.rsplit('_')[0]

# Verifies there is a scammer file for each non scammer file
# Assumes they have the same prefix
def verify_files(scammer_path, non_scammer_path):
  scammer_files = os.listdir(scammer_path)
  non_scammer_files = os.listdir(non_scammer_path)

  if len(scammer_files) is not len(non_scammer_files):
    print('Unequal number of files in data folders. Exiting.')
    exit()
  
  for i in range(len(scammer_files)):
    if get_file_prefix(scammer_files[i]) != get_file_prefix(non_scammer_files[i]):
      print('Could not find corresponding non-scammer file for scammer file: ', scammer_files[i], '. Exiting.')
      exit()
  
  return

# Combines nonscammer and scammer dataframes into single dataframe
def combine_dataframes(scammer_df, non_scammer_df):
  scammer_df['scammer'] = 'Yes'
  non_scammer_df['scammer'] = 'No'

  return pd.concat([scammer_df, non_scammer_df], ignore_index=True)

# Reads data files and writes to single data file
def process_dataset(scammer_path, non_scammer_path, out_dir, name):
  scammer = pd.read_csv(scammer_path)
  non_scammer = pd.read_csv(non_scammer_path)

  all = combine_dataframes(scammer, non_scammer)

  all_name = f'{name}ALL.csv'

  all.to_csv(f'{out_dir}/{all_name}', index=False)

# Walks through a directory with scammer and non scammer folders and processes datafiles
def process_files(scammer_path, non_scammer_path, out_dir):
  verify_files(scammer_path, non_scammer_path)

  scammer_files = os.listdir(scammer_path)
  non_scammer_files = os.listdir(non_scammer_path)

  for s, n in zip(scammer_files, non_scammer_files):
    name = get_file_prefix(s)
    print(f'Processing {name} dataset')
    process_dataset(f'{scammer_path}/{s}', f'{non_scammer_path}/{n}', out_dir, name)



scammer_dir = sys.argv[1] # path to scammer directory
non_scammer_dir = sys.argv[2] # path to non scammer directory
out_dir = sys.argv[3] if len(sys.argv) > 3 else './' # path to output directory

process_files(scammer_dir, non_scammer_dir, out_dir)