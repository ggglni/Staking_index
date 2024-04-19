from flask import Flask, render_template
import pandas as pd
import json
import os
import glob

app = Flask(__name__)

@app.route('/')
def display_data():
    # Find the latest JSON file saved by Script 1
    list_of_files = glob.glob('staking_rewards_data_*.json')
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

    # Filtering rows based on metricKey for 'real_reward_rate' and 'staking_marketcap'
    df_real_reward_rate = df[df['metrics_metricKey'] == 'real_reward_rate']
    df_staking_marketcap = df[df['metrics_metricKey'] == 'staking_marketcap']

    # Merge the two filtered DataFrames on the asset symbol to combine relevant metrics
    merged_df = df_real_reward_rate.merge(df_staking_marketcap, on=['id', 'name', 'symbol'], suffixes=('_rr', '_smc'))

    # Filter merged DataFrame to include only those with a staking market cap >= 1 billion
    filtered_df = merged_df[merged_df['metrics_defaultValue_smc'] >= 1e9]

    # Select specific columns and rename them for display
    display_df = filtered_df[['name', 'symbol', 'metrics_defaultValue_rr', 'metrics_defaultValue_smc']]
    display_df.columns = ['Name', 'Symbol', 'Real Reward Rate', 'Staking Market Cap']

    # Format the columns
    display_df['Real Reward Rate'] = display_df['Real Reward Rate'].apply(lambda x: f"{x:.2%}")
    display_df['Staking Market Cap'] = display_df['Staking Market Cap'].apply(lambda x: f"${x:,.0f}")

    # Convert DataFrame to HTML
    data_html = display_df.to_html(classes="table table-responsive table-striped", border=0, index=False)

    # Render the DataFrame in an HTML template
    return render_template('index.html', data_html=data_html)

if __name__ == "__main__":
    app.run(debug=True)

