# News Scheduler Service

Automated news aggregation service for Trenches that fetches crypto news from multiple sources and populates the backend database.

## Features

- **Multi-source aggregation**: NewsAPI, CryptoPanic, Reddit, and CoinMarketCap
- **Trending token detection**: Automatically identifies trending crypto tokens in news
- **Configurable intervals**: Set custom fetch intervals via environment variables
- **Error resilience**: Auto-retry on failures
- **Deduplication**: Backend prevents duplicate news URLs

## Setup

### 1. Install Dependencies

```bash
cd agents
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `agents/` directory:

```bash
# Required API Keys
NEWS_API_KEY=your_newsapi_key
CRYPTOPANIC_API_KEY=your_cryptopanic_key

# Reddit API (optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=trenches_news_bot/1.0
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# CoinMarketCap (optional)
COIN_MARKET_CAP=your_cmc_api_key

# Backend Configuration
BACKEND_URL=http://localhost:8080
NEWS_FETCH_INTERVAL=300  # Fetch every 5 minutes (in seconds)
```

### 3. Get API Keys

- **NewsAPI**: https://newsapi.org/register
- **CryptoPanic**: https://cryptopanic.com/developers/api/
- **Reddit**: https://www.reddit.com/prefs/apps
- **CoinMarketCap**: https://coinmarketcap.com/api/

## Running the Service

### Manual Start

```bash
cd agents
python3 news_scheduler.py
```

### Using the Startup Script

The news scheduler is automatically started when using the main startup script:

```bash
./start-services.sh
```

### As a Background Service

```bash
cd agents
nohup python3 news_scheduler.py > news_scheduler.log 2>&1 &
```

## How It Works

1. **Fetch**: Every N seconds (default: 300), the scheduler fetches news from all configured sources
2. **Parse**: Extracts source, title, and URL from each news item
3. **Detect Trends**: Scans headlines for trending crypto tokens (BTC, ETH, SOL, etc.)
4. **Post**: Sends batch of news items to backend via `POST /news`
5. **Dedupe**: Backend automatically prevents duplicate URLs using `ON CONFLICT DO NOTHING`

## News Sources

### NewsAPI
- General crypto news from major publications
- Rate limit: 100 requests/day (free tier)
- Returns: Title, URL, published date

### CryptoPanic
- Curated crypto news feed
- Rate limit: Varies by tier
- Returns: Title, URL, sentiment (optional)

### Reddit
- Hot posts from crypto subreddits: r/CryptoCurrency, r/bitcoin, r/CryptoMarkets, r/wallstreetbets
- Rate limit: 60 requests/minute
- Returns: Title, URL, score, comments count

### CoinMarketCap
- Top cryptocurrency listings
- Rate limit: Varies by tier
- Returns: Token name, slug, URL

## Database Schema

The news table in PostgreSQL:

```sql
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_timestamp ON news(timestamp DESC);
```

## Monitoring

Check the console output for:
- ✅ Successfully fetched news count
- 🪙 Trending tokens detected
- ❌ Error messages
- ⏳ Next fetch countdown

Example output:
```
📰 [14:23:45] Fetching news...
✅ Fetched 18 news items
🪙 Trending tokens: BTC, ETH, SOL, DOGE
✅ Posted 12 new items (received 18)
```

## Troubleshooting

### No news items fetched
- Check API keys in `.env` file
- Verify API key quotas haven't been exceeded
- Check internet connectivity

### Backend connection failed
- Ensure Go backend is running on port 8080
- Verify `BACKEND_URL` in `.env`
- Check firewall settings

### Duplicate prevention
- The backend automatically prevents duplicate URLs
- If you see "inserted: 0", all news items already exist in database

## Frontend Integration

Access the news feed at: `http://localhost:3000/news`

Features:
- Real-time news display
- Source badges with color coding
- "Time ago" timestamps
- External link indicators
- Refresh button for manual updates
