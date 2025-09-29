#!/usr/bin/env python3
"""
X (Twitter) Publishing Tool for Trenches Agents
===============================================

This tool allows agents to publish their tweets to actual X (Twitter) accounts.
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import tweepy
from dataclasses import dataclass


@dataclass
class TwitterConfig:
    """Twitter API configuration"""
    api_key: str
    api_secret: str 
    access_token: str
    access_token_secret: str
    bearer_token: str
    rate_limit_enabled: bool = True
    rate_limit_delay: int = 1  # seconds between tweets


class TwitterPublisher:
    """Publishes agent tweets to X (Twitter)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        self.client = None
        self.api = None
        self.last_tweet_time = {}  # Track last tweet time per agent
        self.rate_limit_delay = self.config.rate_limit_delay if self.config else 1
        
    def _load_config(self) -> Optional[TwitterConfig]:
        """Load Twitter API configuration from environment"""
        try:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                self.logger.warning("Twitter API credentials not found in environment")
                return None
                
            return TwitterConfig(
                api_key=api_key,
                api_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                bearer_token=bearer_token
            )
        except Exception as e:
            self.logger.error(f"Failed to load Twitter config: {e}")
            return None
    
    async def initialize(self) -> bool:
        """Initialize Twitter API clients"""
        if not self.config:
            self.logger.error("No Twitter configuration available")
            return False
            
        try:
            # Initialize tweepy v2 client
            self.client = tweepy.Client(
                bearer_token=self.config.bearer_token,
                consumer_key=self.config.api_key,
                consumer_secret=self.config.api_secret,
                access_token=self.config.access_token,
                access_token_secret=self.config.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Initialize v1.1 API for additional features if needed
            auth = tweepy.OAuth1UserHandler(
                self.config.api_key,
                self.config.api_secret,
                self.config.access_token,
                self.config.access_token_secret
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Test the connection
            me = self.client.get_me()
            self.logger.info(f"✅ Connected to Twitter as @{me.data.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API: {e}")
            return False
    
    async def publish_tweet(self, agent_id: str, content: str, reply_to_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Publish a tweet to X (Twitter)
        
        Args:
            agent_id: ID of the agent posting the tweet
            content: Tweet content (max 280 characters)
            reply_to_id: ID of tweet to reply to (optional)
            
        Returns:
            Dict with tweet info or None if failed
        """
        if not self.client:
            self.logger.error("Twitter client not initialized")
            return None
            
        try:
            # Rate limiting check
            await self._check_rate_limit(agent_id)
            
            # Ensure content fits Twitter's character limit
            content = self._prepare_content(content)
            
            # Add agent attribution if desired
            attributed_content = self._add_agent_attribution(content, agent_id)
            
            # Post the tweet
            if reply_to_id:
                response = self.client.create_tweet(
                    text=attributed_content,
                    in_reply_to_tweet_id=reply_to_id
                )
            else:
                response = self.client.create_tweet(text=attributed_content)
            
            self.last_tweet_time[agent_id] = datetime.now()
            
            tweet_info = {
                'id': response.data['id'],
                'text': attributed_content,
                'agent_id': agent_id,
                'created_at': datetime.now().isoformat(),
                'url': f"https://twitter.com/user/status/{response.data['id']}"
            }
            
            self.logger.info(f"✅ Published tweet from {agent_id}: {content[:50]}...")
            return tweet_info
            
        except tweepy.TooManyRequests:
            self.logger.warning("Twitter rate limit exceeded, will retry later")
            return None
        except tweepy.Forbidden as e:
            self.logger.error(f"Twitter API forbidden: {e}")
            return None
        except tweepy.Unauthorized:
            self.logger.error("Twitter API unauthorized - check credentials")
            return None
        except Exception as e:
            self.logger.error(f"Failed to publish tweet: {e}")
            return None
    
    async def _check_rate_limit(self, agent_id: str):
        """Check and enforce rate limiting"""
        if not self.config.rate_limit_enabled:
            return
            
        last_time = self.last_tweet_time.get(agent_id)
        if last_time:
            time_diff = (datetime.now() - last_time).total_seconds()
            if time_diff < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_diff
                await asyncio.sleep(sleep_time)
    
    def _prepare_content(self, content: str) -> str:
        """Prepare content for Twitter (handle character limits, etc.)"""
        # Twitter character limit
        max_length = 280
        
        # If content is too long, truncate with ellipsis
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
            
        return content
    
    def _add_agent_attribution(self, content: str, agent_id: str) -> str:
        """Add agent attribution to tweet (optional)"""
        # You can customize this based on your preference
        # Options:
        # 1. No attribution (return content as-is)
        # 2. Add hashtag
        # 3. Add signature
        
        # Option 1: No attribution (agents post as the main account)
        return content
        
        # Option 2: Add hashtag (uncomment if desired)
        # return f"{content} #TrenchesAI"
        
        # Option 3: Add agent signature (uncomment if desired)
        # return f"{content}\n\n- {agent_id.replace('_', ' ').title()}"
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get current account information"""
        if not self.client:
            return None
            
        try:
            me = self.client.get_me(user_fields=['public_metrics'])
            return {
                'username': me.data.username,
                'name': me.data.name,
                'id': me.data.id,
                'followers_count': me.data.public_metrics['followers_count'],
                'following_count': me.data.public_metrics['following_count'],
                'tweet_count': me.data.public_metrics['tweet_count']
            }
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return None


# Tool function for use in agent system
async def publish_to_twitter(agent_id: str, content: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool function to publish agent tweets to X (Twitter)
    
    Args:
        agent_id: ID of the agent posting
        content: Tweet content
        reply_to_id: Optional tweet ID to reply to
        
    Returns:
        Dict with result status and info
    """
    publisher = TwitterPublisher()
    
    if not await publisher.initialize():
        return {
            'success': False,
            'error': 'Failed to initialize Twitter API',
            'published': False
        }
    
    result = await publisher.publish_tweet(agent_id, content, reply_to_id)
    
    if result:
        return {
            'success': True,
            'published': True,
            'tweet_info': result,
            'message': f'Successfully published to Twitter: {result["url"]}'
        }
    else:
        return {
            'success': False,
            'published': False,
            'error': 'Failed to publish tweet to Twitter'
        }


# Example usage and testing
async def test_twitter_publisher():
    """Test the Twitter publisher"""
    publisher = TwitterPublisher()
    
    if not await publisher.initialize():
        print("❌ Failed to initialize Twitter API")
        return
    
    # Get account info
    account_info = await publisher.get_account_info()
    if account_info:
        print(f"✅ Connected to @{account_info['username']} ({account_info['followers_count']} followers)")
    
    # Test tweet
    test_content = "🚀 Testing Trenches AI agent system! The future of autonomous social media is here. #AI #Crypto #TrenchesAI"
    
    result = await publisher.publish_tweet("test_agent", test_content)
    if result:
        print(f"✅ Test tweet published: {result['url']}")
    else:
        print("❌ Failed to publish test tweet")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_twitter_publisher())