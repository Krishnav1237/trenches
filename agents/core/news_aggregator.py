import random

def get_aggregated_news(limit=5):
    """
    Placeholder news aggregator.
    Always returns a flat list of dicts with 'title' keys.
    Replace with real API or scraping logic.
    """
    sample_news = [
        {"title": "BTC surges 5% after ETF approval"},
        {"title": "ETH network upgrade boosts transaction speed"},
        {"title": "Crypto market sees mixed trends"},
        {"title": "BTC price stabilizes at $60,000"},
        {"title": "ETH gas fees drop to monthly low"},
    ]
    random.shuffle(sample_news)
    return sample_news[:limit]
