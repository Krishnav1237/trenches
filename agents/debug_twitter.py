#!/usr/bin/env python3
"""
Debug Twitter API Connection
"""

import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Debugging Twitter API Connection")
print("=" * 40)

# Check credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

print(f"API Key: {api_key[:10]}..." if api_key else "❌ Missing")
print(f"API Secret: {api_secret[:10]}..." if api_secret else "❌ Missing")
print(f"Access Token: {access_token[:10]}..." if access_token else "❌ Missing")
print(f"Access Token Secret: {access_token_secret[:10]}..." if access_token_secret else "❌ Missing")
print(f"Bearer Token: {bearer_token[:10]}..." if bearer_token else "❌ Missing")

print("\n🧪 Testing Bearer Token Only...")
try:
    client = tweepy.Client(bearer_token=bearer_token)
    me = client.get_me()
    print(f"✅ Bearer Token works! Connected as: {me.data.username}")
except Exception as e:
    print(f"❌ Bearer Token failed: {e}")

print("\n🧪 Testing Full OAuth...")
try:
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    me = client.get_me()
    print(f"✅ Full OAuth works! Connected as: {me.data.username}")
    print(f"   Followers: {me.data.public_metrics['followers_count'] if hasattr(me.data, 'public_metrics') else 'N/A'}")
except Exception as e:
    print(f"❌ Full OAuth failed: {e}")

print("\n🧪 Testing v1.1 API...")
try:
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    me = api.verify_credentials()
    print(f"✅ v1.1 API works! Connected as: @{me.screen_name}")
except Exception as e:
    print(f"❌ v1.1 API failed: {e}")