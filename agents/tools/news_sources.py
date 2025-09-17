_all_ = ["get_aggregated_news"]
import os
import requests
import praw
from tools.reddit_scraper import fetch_reddit_posts
from dotenv import load_dotenv
load_dotenv()

def fetch_from_coinmarketcap(query="crypto", limit=3):
    key = os.getenv("COIN_MARKET_CAP")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    try:
        resp = requests.get(url, params={
            "start": 1,
            "limit": limit,
            "convert": "USD",
            "CMC_PRO_API_KEY": key
        })
        resp.raise_for_status()
        return [{"source": "CoinMarketCap", "title": a["name"], "url": f"https://coinmarketcap.com/currencies/{a['slug']}"} for a in resp.json().get("data", [])]
    except Exception as e:
        return [{"source": "CoinMarketCap", "error": str(e)}]

def fetch_from_newsapi(query="crypto", limit=3):
    key = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/everything"
    try:
        resp = requests.get(url, params={
            "q": query,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": key
        })
        resp.raise_for_status()
        return [{"source": "NewsAPI", "title": a["title"], "url": a["url"]} for a in resp.json().get("articles", [])]
    except Exception as e:
        return [{"source": "NewsAPI", "error": str(e)}]

def fetch_from_cryptopanic(limit=3):
    key = os.getenv("CRYPTOPANIC_API_KEY")
    url = "https://cryptopanic.com/api/developer/v2/posts/"
    try:
        resp = requests.get(url, params={
            "auth_token": key,
            "filter": "news",
            "public": "true"
        })
        resp.raise_for_status()
        return [
            {
                "source": "CryptoPanic",
                "title": item.get("title", "No Title"),
                "url": item.get("url")
            }
            for item in resp.json().get("results", [])[:limit]
        ]
    except Exception as e:
        return [{"source": "CryptoPanic", "error": str(e)}]

import praw
import os

import os
import praw

def fetch_from_reddit(limit=5):
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            check_for_async=False
        )

      
        print(f"👤 Reddit logged in as: {reddit.user.me()}")

        subreddit = reddit.subreddit("CryptoCurrency+bitcoin+CryptoMarkets+wallstreetbets")
        posts = []

        for post in subreddit.hot(limit=limit):
            posts.append({
                "source": "Reddit",
                "title": post.title,
                "url": post.url
            })

        return posts
    except Exception as e:
        print(f"❌ Reddit error: {e}")
        return []


def get_aggregated_news(limit=3):
    all_news = []
    all_news += fetch_from_newsapi(limit=limit)
    all_news += fetch_from_cryptopanic(limit=limit)
    all_news += fetch_from_reddit(limit=limit)
    all_news += fetch_from_coinmarketcap(limit=limit)
    
    # Flatten in case any fetcher returns nested lists
    flat_news = []
    for item in all_news:
        if isinstance(item, list):
            flat_news.extend(item)  # unpack inner list
        else:
            flat_news.append(item)
    
    tokens = detect_trending_tokens(flat_news)
    print(f"🪙 Trending tokens found: {tokens}")

    # Try Reddit tool as a fallback
    try:
        reddit_news = fetch_reddit_posts(limit=limit)
        for r in reddit_news:
            flat_news.append({
                "source": "Reddit",
                "title": r["title"],
                "url": r["url"]
            })
    except Exception as e:
        print(f"❌ Reddit error: {e}")

    return flat_news, tokens

    

def detect_trending_tokens(news_items):
    """
    Extracts crypto token symbols or names from a list of news item dicts.
    Looks into title and content/summary fields.
    """
    keywords = [
        'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol', 'xrp',
        'shiba', 'shib', 'pepe', 'blockdag', 'litecoin', 'ltc',
        'dogecoin', 'doge', 'bnb', 'cardano', 'ada', 'polkadot', 'dot'
    ]
    
    found = set()
    
    for item in news_items:
        if not item:
            continue
        
        text_parts = [
            item.get("title", ""), 
            item.get("content", ""), 
            item.get("description", "")  # for NewsAPI
        ]
        full_text = " ".join(text_parts).lower()
        
        for keyword in keywords:
            if keyword in full_text:
                found.add(keyword.upper())
    
    return list(found)