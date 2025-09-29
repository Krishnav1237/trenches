#!/usr/bin/env python3
"""
Simple Twitter Publisher using v1.1 API
========================================

Since your v1.1 API is working, let's use that for posting tweets.
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SimpleTwitterPublisher:
    """Simple Twitter publisher using v1.1 API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api = None
        self.last_tweet_time = {}
        self.rate_limit_delay = 1  # seconds between tweets
        
    async def initialize(self) -> bool:
        """Initialize Twitter API v1.1"""
        try:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                self.logger.error("Missing Twitter API credentials")
                return False
            
            # Initialize v1.1 API
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Test connection
            me = self.api.verify_credentials()
            self.logger.info(f"✅ Connected to Twitter as @{me.screen_name}")
            print(f"✅ Connected to Twitter as @{me.screen_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API: {e}")
            return False
    
    async def publish_tweet(self, agent_id: str, content: str) -> Optional[Dict[str, Any]]:
        """Publish a tweet using v1.1 API"""
        if not self.api:
            self.logger.error("Twitter API not initialized")
            return None
            
        try:
            # Rate limiting
            await self._check_rate_limit(agent_id)
            
            # Prepare content
            content = self._prepare_content(content)
            
            # Post tweet
            tweet = self.api.update_status(content)
            
            self.last_tweet_time[agent_id] = datetime.now()
            
            tweet_info = {
                'id': tweet.id_str,
                'text': tweet.text,
                'agent_id': agent_id,
                'created_at': tweet.created_at.isoformat(),
                'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
            }
            
            self.logger.info(f"✅ Published tweet from {agent_id}: {content[:50]}...")
            print(f"✅ Published: {tweet_info['url']}")
            return tweet_info
            
        except tweepy.TooManyRequests:
            self.logger.warning("Twitter rate limit exceeded")
            return None
        except Exception as e:
            self.logger.error(f"Failed to publish tweet: {e}")
            return None
    
    async def _check_rate_limit(self, agent_id: str):
        """Check rate limiting"""
        last_time = self.last_tweet_time.get(agent_id)
        if last_time:
            time_diff = (datetime.now() - last_time).total_seconds()
            if time_diff < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_diff
                await asyncio.sleep(sleep_time)
    
    def _prepare_content(self, content: str) -> str:
        """Prepare content for Twitter"""
        if len(content) > 280:
            content = content[:277] + "..."
        return content
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information"""
        if not self.api:
            return None
            
        try:
            me = self.api.verify_credentials()
            return {
                'username': me.screen_name,
                'name': me.name,
                'id': me.id_str,
                'followers_count': me.followers_count,
                'friends_count': me.friends_count,
                'statuses_count': me.statuses_count
            }
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return None


# Test function
async def test_simple_publisher():
    """Test the simple Twitter publisher"""
    print("🧪 Testing Simple Twitter Publisher")
    print("=" * 40)
    
    publisher = SimpleTwitterPublisher()
    
    if not await publisher.initialize():
        print("❌ Failed to initialize")
        return
    
    # Get account info
    account_info = await publisher.get_account_info()
    if account_info:
        print(f"Account: @{account_info['username']} ({account_info['followers_count']} followers)")
    
    # Test tweet
    test_content = "🚀 Testing Trenches AI agent system! The bots are coming to life! #TrenchesAI #AI #Crypto"
    
    result = await publisher.publish_tweet("test_agent", test_content)
    if result:
        print(f"✅ Test tweet successful!")
        print(f"URL: {result['url']}")
    else:
        print("❌ Test tweet failed")


if __name__ == "__main__":
    asyncio.run(test_simple_publisher())