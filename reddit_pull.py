# Load in depdencies
import pandas as pd
import requests
from datetime import datetime
import os 

# Read credentials from environment variables
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('SECRET_KEY')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# Check if all environment variables are set
if not all([client_id, client_secret, username, password]):
    raise ValueError("Some of the required environment variables are missing.")


# Get the current date to append to the backup filenames
current_date = datetime.now().strftime('%Y-%m-%d')

## Load in historic data
btc_r = pd.read_csv('Data/BTC_R.csv')
eth_r = pd.read_csv('Data/ETH_R.csv')
sol_r = pd.read_csv('Data/SOL_R.csv')

# Save backups
btc_r.to_csv(f'Data/Backup/BTC_R_{current_date}.csv', index=False)
eth_r.to_csv(f'Data/Backup/ETH_R_{current_date}.csv', index=False)
sol_r.to_csv(f'Data/Backup/SOL_R_{current_date}.csv', index=False)


# Convert to date
btc_r.date_posted = pd.to_datetime(btc_r.date_posted, format='mixed', dayfirst=False)
eth_r.date_posted = pd.to_datetime(eth_r.date_posted, format='mixed', dayfirst=False)
sol_r.date_posted = pd.to_datetime(sol_r.date_posted, format='mixed', dayfirst=False)


print(btc_r)
print(eth_r)
print(sol_r)

# API Authentication
CLIENT_ID = client_id
SECRET_KEY = client_secret 


auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
data = {
    'grant_type': 'password',
    'username': username,
    'password': password
}

headers = {'User-Agent': 'SolanaAPI/0.1'}
res = requests.post('https://www.reddit.com/api/v1/access_token',
                  auth=auth, data=data, headers=headers)
TOKEN = res.json()['access_token']
headers = {**headers, **{'Authorization': f'bearer {TOKEN}'}}

# Pull Subreddit Data
res_bitcoin = requests.get('https://oauth.reddit.com/r/bitcoin/hot?limit=100',
                  headers = headers)

res_solana = requests.get('https://oauth.reddit.com/r/solana/hot?limit=100',
                  headers = headers)

res_eth = requests.get('https://oauth.reddit.com/r/ethereum/hot?limit=100',
                  headers = headers)

# Make function to process the API Pull
def process_posts(json_data):
    # Initialize an empty list to store post data
    posts_data = []

    # Loop through each post in the JSON data
    for post in json_data['data']['children']:
        # Convert the Unix timestamp to a datetime object
        created_date = datetime.fromtimestamp(post['data']['created_utc']).strftime('%m/%d/%y')

        # Get the current system date
        pull_date = datetime.now().strftime('%m/%d/%y')

        # Append the data as a dictionary to the list
        posts_data.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            'comments': post['data']['num_comments'],
            'date_posted': created_date,
            'pull_date': pull_date  # Add the pull_date to the data
        })

    # Convert the list of dictionaries to a DataFrame
    return pd.DataFrame(posts_data)

btc_reddit_new = process_posts(res_bitcoin.json())
eth_reddit_new = process_posts(res_eth.json())
sol_reddit_new = process_posts(res_solana.json())

btc = pd.concat([btc_r, btc_reddit_new], axis = 0)
eth = pd.concat([eth_r, eth_reddit_new], axis = 0)
sol = pd.concat([sol_r, sol_reddit_new], axis = 0)


def clean_df(df):
    clean = df.copy()
    clean = clean[['subreddit','title', 'selftext', 'upvote_ratio', 'ups', 'downs', 'score', 'comments', 'date_posted', 'pull_date']]
    return clean

btc, eth, sol = clean_df(btc), clean_df(eth), clean_df(sol)

btc.to_csv('Data/BTC_R.csv', index=False)
eth.to_csv('Data/ETH_R.csv', index=False)
sol.to_csv('Data/SOL_R.csv', index=False)