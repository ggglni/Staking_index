import requests
import json
from datetime import datetime

# The API endpoint for making the request
endpoint = "https://api.stakingrewards.com/public/query"

# GraphQL query specifying what data to fetch
query = """
query {
  assets(limit: 50) {
    id
    name
    slug
    symbol
    metrics(
        where: { metricKeys: [
            "real_reward_rate"
            "reward_rate"
            "inflation_rate"
            "marketcap"
            "staking_marketcap"
            "price"
            "price_roi_365d"
            ]}
        limit: 100) {
      metricKey
      unit
      defaultValue
      changePercentages
    }    
  }
}
"""

# Headers including the content type and your API key
headers = {
  "Content-Type": "application/json",
  "X-API-KEY": "aac41124-db1b-4a6a-98c1-268f3c1d3973",  # Remember to secure your API key properly in production
}

# Data to be sent with POST request, wrapped in a dictionary
data = {"query": query}

# Making the POST request
response = requests.post(endpoint, json=data, headers=headers)

# Checking the response and handling accordingly
if response.status_code == 200:
    # If the request was successful, print the JSON data
    response_data = response.json()
    print(response_data)
    
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'staking_rewards_data_{timestamp}.json'
    
    # Save the response data to a JSON file with the timestamp in the filename
    with open(filename, 'w') as file:
        json.dump(response_data, file, indent=4)
    print(f'Data successfully saved to {filename}')
else:
    # If the request failed, print an error message and the status code
    print("Error occurred:", response.status_code)
