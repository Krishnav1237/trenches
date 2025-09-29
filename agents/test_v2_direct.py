#!/usr/bin/env python3
"""
Direct Twitter v2 API Test
"""

import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

print("🧪 Testing Twitter v2 API Direct")
print("=" * 40)

# Get credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

print(f"Credentials loaded: {bool(all([api_key, api_secret, access_token, access_token_secret, bearer_token]))}")

try:
    # Test v2 API with full credentials
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True
    )
    
    print("✅ Client created successfully")
    
    # Test getting user info
    me = client.get_me()
    print(f"✅ User info: {me.data.username}")
    
    # Test posting a simple tweet
    test_tweet = "🚀 Testing Trenches AI agent system! The bots are coming to life! #TrenchesAI #Test"
    
    print(f"📤 Attempting to post: {test_tweet}")
    
    response = client.create_tweet(text=test_tweet)
    
    if response.data:
        tweet_id = response.data['id']
        print(f"✅ SUCCESS! Tweet posted!")
        print(f"🔗 URL: https://twitter.com/Rudraps_2005/status/{tweet_id}")
        print(f"📝 Tweet ID: {tweet_id}")
    else:
        print("❌ No data in response")
        print(f"Response: {response}")
        
except tweepy.Forbidden as e:
    print(f"❌ Forbidden Error: {e}")
    print("\nThis means your app still doesn't have the right access level.")
    print("You might need to:")
    print("1. Apply for Elevated access")
    print("2. Or check if your project setup is correct")
    
except tweepy.Unauthorized as e:
    print(f"❌ Unauthorized: {e}")
    print("Check your tokens again")
    
except Exception as e:
    print(f"❌ Other error: {e}")
    print(f"Error type: {type(e)}")