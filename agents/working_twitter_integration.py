#!/usr/bin/env python3
"""
🎉 WORKING Twitter Integration for Trenches Agents!
==================================================

This is the FINAL working version that will post your agent tweets to X!
"""

import os
import time
import asyncio
import logging
import random
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WorkingTwitterPublisher:
    """WORKING Twitter publisher using v2 API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.last_tweet_time = {}
        self.rate_limit_delay = 3  # 3 seconds between tweets to be safe
        
    async def initialize(self) -> bool:
        """Initialize Twitter API v2"""
        try:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
                self.logger.error("Missing Twitter API credentials")
                return False
            
            # Initialize v2 Client (THIS IS THE WORKING VERSION!)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Test connection
            me = self.client.get_me()
            self.logger.info(f"✅ Connected to Twitter as @{me.data.username}")
            print(f"🐦 ✅ CONNECTED TO X: @{me.data.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API: {e}")
            return False
    
    async def publish_tweet(self, agent_id: str, content: str) -> Optional[Dict[str, Any]]:
        """Publish a tweet to X using v2 API"""
        if not self.client:
            self.logger.error("Twitter client not initialized")
            return None
            
        try:
            # Rate limiting
            await self._check_rate_limit(agent_id)
            
            # Prepare content
            content = self._prepare_content(content)
            
            # Add agent signature (optional)
            final_content = self._add_signature(content, agent_id)
            
            # Post tweet using v2 API
            response = self.client.create_tweet(text=final_content)
            
            self.last_tweet_time[agent_id] = datetime.now()
            
            if response.data:
                tweet_id = response.data['id']
                tweet_info = {
                    'id': tweet_id,
                    'text': final_content,
                    'agent_id': agent_id,
                    'created_at': datetime.now().isoformat(),
                    'url': f"https://twitter.com/Rudraps_2005/status/{tweet_id}"
                }
                
                self.logger.info(f"✅ Published tweet from {agent_id}")
                print(f"🐦 ✅ POSTED TO X: {final_content[:50]}...")
                print(f"🔗 URL: {tweet_info['url']}")
                return tweet_info
            else:
                self.logger.error("No data in Twitter response")
                return None
            
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
                print(f"⏰ Rate limiting: waiting {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
    
    def _prepare_content(self, content: str) -> str:
        """Prepare content for Twitter"""
        # Twitter character limit
        max_length = 270  # Leave some room for signature
        
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
            
        return content
    
    def _add_signature(self, content: str, agent_id: str) -> str:
        """Add signature to tweet"""
        # Option 1: No signature (clean tweets)
        return content
        
        # Option 2: Add hashtag (uncomment if you want)
        # return f"{content}\n\n#TrenchesAI"
        
        # Option 3: Add agent info (uncomment if you want)
        # agent_name = agent_id.replace('_', ' ').replace('agent ', '').title()
        # return f"{content}\n\n- {agent_name}"
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information"""
        if not self.client:
            return None
            
        try:
            me = self.client.get_me(user_fields=['public_metrics'])
            return {
                'username': me.data.username,
                'name': me.data.name,
                'id': me.data.id,
                'followers_count': me.data.public_metrics['followers_count'] if hasattr(me.data, 'public_metrics') else 0,
                'following_count': me.data.public_metrics['following_count'] if hasattr(me.data, 'public_metrics') else 0,
                'tweet_count': me.data.public_metrics['tweet_count'] if hasattr(me.data, 'public_metrics') else 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return None


# Demo function to test with sample agent tweets
async def demo_agent_twitter_integration():
    """Demo your working Twitter integration!"""
    print("🚀 TRENCHES → X INTEGRATION DEMO")
    print("=" * 50)
    
    publisher = WorkingTwitterPublisher()
    
    if not await publisher.initialize():
        print("❌ Failed to initialize Twitter")
        return
    
    # Sample agent tweets
    agent_tweets = [
        {
            'agent_id': 'CryptoDegen_Alpha',
            'tweet': '🚀 BTC breaking through resistance! The bulls are back! This could be the start of the next leg up! 💎🙌 #Bitcoin #BTC'
        },
        {
            'agent_id': 'SolanaMaxi_Pro', 
            'tweet': 'SOL ecosystem is on fire right now! DeFi TVL hitting new highs, new projects launching daily. Still early! 🌞 #Solana #DeFi'
        },
        {
            'agent_id': 'AIAgentAlpha',
            'tweet': 'The AI + Crypto narrative is just getting started. Autonomous agents trading, analyzing, and posting. The future is here! 🤖 #AI #Crypto'
        }
    ]
    
    print(f"\n🤖 Publishing {len(agent_tweets)} agent tweets to X...")
    published_count = 0
    
    for tweet_data in agent_tweets:
        result = await publisher.publish_tweet(
            tweet_data['agent_id'], 
            tweet_data['tweet']
        )
        
        if result:
            published_count += 1
            print(f"✅ Success! Tweet {published_count}/{len(agent_tweets)}")
        else:
            print(f"❌ Failed to publish tweet from {tweet_data['agent_id']}")
        
        # Wait between tweets
        if tweet_data != agent_tweets[-1]:  # Don't wait after last tweet
            await asyncio.sleep(2)
    
    print(f"\n🎉 DEMO COMPLETE!")
    print(f"📊 Published: {published_count}/{len(agent_tweets)} tweets")
    print(f"🔗 Check your X account: https://twitter.com/Rudraps_2005")
    
    # Get account stats
    account_info = await publisher.get_account_info()
    if account_info:
        print(f"\n📈 Account Stats:")
        print(f"   👥 Followers: {account_info['followers_count']}")
        print(f"   📝 Total Tweets: {account_info['tweet_count']}")


if __name__ == "__main__":
    asyncio.run(demo_agent_twitter_integration())