import requests
import json

# Access token and Instagram user ID (replace with your values)
access_token = 'YOUR_ACCESS_TOKEN'
user_id = 'YOUR_USER_ID'

# Base URL for Instagram Graph API
base_url = 'https://graph.instagram.com/'

# Function to fetch user profile
def fetch_user_profile(user_id, access_token):
    url = f'{base_url}{user_id}?fields=id,username,account_type,media_count&access_token={access_token}'
    response = requests.get(url)
    return response.json()

# Function to fetch user media
def fetch_user_media(user_id, access_token):
    url = f'{base_url}{user_id}/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp&access_token={access_token}'
    response = requests.get(url)
    return response.json()

# Fetch and print user profile
user_profile = fetch_user_profile(user_id, access_token)
print(json.dumps(user_profile, indent=4))

# Fetch and print user media
user_media = fetch_user_media(user_id, access_token)
print(json.dumps(user_media, indent=4))
