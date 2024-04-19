import pandas as pd
import json
import os
import glob

# Find the latest JSON file saved by Script 1
list_of_files = glob.glob('staking_rewards_data_*.json')  # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print(f"Processing file: {latest_file}")

# Load data from the latest JSON file
with open(latest_file, 'r') as file:
    data = json.load(file)

# Normalize data to flatten the structure into a DataFrame
df = pd.json_normalize(data['data']['assets'], record_path=['metrics'], meta=['id', 'name', 'symbol'],
                       record_prefix='metrics_')

# Convert the defaultValue to float for numeric operations
df['metrics_defaultValue'] = df['metrics_defaultValue'].astype(float)

# List of metrics of interest
metrics_list = ['real_reward_rate', 'inflation_rate', 'reward_rate', 'marketcap', 'staking_marketcap']

# Create a DataFrame dictionary for easier merging
dfs = {}
for metric in metrics_list:
    # Select and rename the columns to avoid collision and preserve necessary data
    temp_df = df[df['metrics_metricKey'] == metric][['id', 'name', 'symbol', 'metrics_defaultValue']]
    temp_df.rename(columns={'metrics_defaultValue': f'{metric}_value'}, inplace=True)
    dfs[metric] = temp_df

# Perform an iterative merge (left join) on all metrics DataFrames
from functools import reduce
def merge_dfs(x, y):
    return pd.merge(x, y, on=['id', 'name', 'symbol'], how='left', suffixes=('', '_drop'))

final_df = reduce(merge_dfs, dfs.values())

# Remove columns that may have been duplicated and retained '_drop' suffix
final_df = final_df[[col for col in final_df.columns if not col.endswith('_drop')]]

# Filter final DataFrame to include only those with a staking market cap >= 1 billion
final_filtered_df = final_df[final_df['staking_marketcap_value'] >= 1e9]

# Sorting the filtered DataFrame by 'defaultValue' of 'real_reward_rate'
sorted_df = final_filtered_df.sort_values(by='real_reward_rate_value', ascending=False)

# Display the sorted DataFrame
print(sorted_df[['id', 'name', 'symbol', 'real_reward_rate_value', 'inflation_rate_value', 'reward_rate_value', 'marketcap_value', 'staking_marketcap_value']])
