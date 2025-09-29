#!/usr/bin/env python3
"""
X (Twitter) Integration Setup Script
===================================

This script helps you set up X (Twitter) API integration for your Trenches agents.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from tools.twitter_publisher import TwitterPublisher

# Load environment variables
load_dotenv()


async def setup_twitter_integration():
    """Interactive setup for Twitter integration"""
    print("🐦 X (Twitter) API Integration Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        # Copy from .env.example
        example_file = Path('.env.example')
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found")
            return
    
    # Check current credentials
    print("\n🔑 Checking X API Credentials...")
    
    credentials = {
        'TWITTER_API_KEY': os.getenv('TWITTER_API_KEY'),
        'TWITTER_API_SECRET': os.getenv('TWITTER_API_SECRET'),
        'TWITTER_ACCESS_TOKEN': os.getenv('TWITTER_ACCESS_TOKEN'),
        'TWITTER_ACCESS_TOKEN_SECRET': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN')
    }
    
    missing_creds = [k for k, v in credentials.items() if not v or v.startswith('your_')]
    
    if missing_creds:
        print(f"❌ Missing credentials: {', '.join(missing_creds)}")
        print("\n📋 To get X API credentials:")
        print("1. Go to https://developer.twitter.com")
        print("2. Apply for Developer Account")
        print("3. Create a new App/Project")
        print("4. Generate API Keys and Tokens")
        print("5. Add them to your .env file")
        print("\n💡 Make sure to enable 'Read and Write' permissions!")
        return False
    else:
        print("✅ All credentials found")
    
    # Test connection
    print("\n🧪 Testing X API Connection...")
    publisher = TwitterPublisher()
    
    if await publisher.initialize():
        account_info = await publisher.get_account_info()
        if account_info:
            print(f"✅ Successfully connected to @{account_info['username']}")
            print(f"   Followers: {account_info['followers_count']:,}")
            print(f"   Following: {account_info['following_count']:,}")
            print(f"   Tweets: {account_info['tweet_count']:,}")
            
            # Ask about test tweet
            response = input("\n🧪 Would you like to post a test tweet? (y/n): ").lower().strip()
            if response == 'y':
                test_content = "🚀 Testing Trenches AI agent system integration with X! The future is here. #TrenchesAI #AI #Crypto"
                
                result = await publisher.publish_tweet("setup_test", test_content)
                if result:
                    print(f"✅ Test tweet posted successfully!")
                    print(f"   URL: {result['url']}")
                else:
                    print("❌ Failed to post test tweet")
            
            return True
        else:
            print("❌ Connected but couldn't get account info")
            return False
    else:
        print("❌ Failed to connect to X API")
        print("   Check your credentials in .env file")
        return False


async def configure_publishing_settings():
    """Configure publishing settings"""
    print("\n⚙️  Publishing Configuration")
    print("=" * 30)
    
    settings = {
        'tweet_selection_rate': 0.3,  # 30% of tweets go to X
        'rate_limit_delay': 1,  # seconds between tweets
        'quality_filters': True,
        'agent_attribution': False,  # whether to add agent names to tweets
    }
    
    print(f"Current settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    # You can add interactive configuration here if needed
    print("\n💡 You can modify these settings in enhanced_simulation.py")
    
    return settings


async def show_usage_examples():
    """Show usage examples"""
    print("\n📚 Usage Examples")
    print("=" * 20)
    
    print("1. Run Enhanced Simulation with X Integration:")
    print("   python enhanced_simulation.py")
    
    print("\n2. Test Twitter Publisher:")
    print("   python -c \"from tools.twitter_publisher import test_twitter_publisher; import asyncio; asyncio.run(test_twitter_publisher())\"")
    
    print("\n3. Check Current Settings:")
    print("   python twitter_setup.py")
    
    print("\n4. Manual Tweet (in Python):")
    print("   from tools.twitter_publisher import publish_to_twitter")
    print("   result = await publish_to_twitter('agent_id', 'Tweet content')")


async def main():
    """Main setup function"""
    print("🕳️  Trenches X (Twitter) Integration Setup")
    print("=" * 50)
    
    # Setup Twitter integration
    success = await setup_twitter_integration()
    
    if success:
        # Configure settings
        await configure_publishing_settings()
        
        # Show usage examples
        await show_usage_examples()
        
        print("\n🎉 Setup Complete!")
        print("Your agents can now post to X (Twitter)!")
        print("\n▶️  Next steps:")
        print("1. Run: python enhanced_simulation.py")
        print("2. Watch your agents post to X!")
        
    else:
        print("\n❌ Setup failed. Please check your API credentials.")


if __name__ == "__main__":
    asyncio.run(main())