#!/usr/bin/env python3
"""
News Scheduler Service for Trenches
Periodically fetches crypto news from multiple sources and posts to backend
"""

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.news_sources import get_aggregated_news

load_dotenv()

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
FETCH_INTERVAL = int(os.getenv("NEWS_FETCH_INTERVAL", "300"))  # 5 minutes default

class NewsScheduler:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.fetch_interval = FETCH_INTERVAL

    def fetch_and_post_news(self):
        """Fetch news from all sources and post to backend"""
        try:
            print(f"📰 [{datetime.now().strftime('%H:%M:%S')}] Fetching news...")

            # Get aggregated news from all sources
            news_items, trending_tokens = get_aggregated_news(limit=5)

            if not news_items:
                print("⚠️  No news items fetched")
                return

            # Filter out error items
            valid_news = [
                item for item in news_items
                if 'error' not in item and item.get('title') and item.get('url')
            ]

            if not valid_news:
                print("⚠️  No valid news items to post")
                return

            print(f"✅ Fetched {len(valid_news)} news items")
            if trending_tokens:
                print(f"🪙 Trending tokens: {', '.join(trending_tokens)}")

            # Post to backend
            response = requests.post(
                f"{self.backend_url}/news",
                json=valid_news,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Posted {result.get('inserted', 0)} new items (received {result.get('received', 0)})")
            else:
                print(f"❌ Failed to post news: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Error fetching/posting news: {e}")

    def run(self):
        """Run the scheduler in a continuous loop"""
        print(f"🚀 News Scheduler started")
        print(f"📡 Backend URL: {self.backend_url}")
        print(f"⏱️  Fetch interval: {self.fetch_interval} seconds")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Fetch immediately on startup
        self.fetch_and_post_news()

        # Then run on interval
        while True:
            try:
                time.sleep(self.fetch_interval)
                self.fetch_and_post_news()
            except KeyboardInterrupt:
                print("\n🛑 News Scheduler stopped")
                break
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                print("⏳ Retrying in 60 seconds...")
                time.sleep(60)

def main():
    """Main entry point"""
    scheduler = NewsScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()
