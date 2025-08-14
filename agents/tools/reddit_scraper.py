# tools/reddit_scraper.py

import os
import praw

def fetch_reddit_posts(subreddit_name="CryptoCurrency", limit=5):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for submission in subreddit.hot(limit=limit):
        posts.append({
            "title": submission.title,
            "url": submission.url,
            "score": submission.score,
            "comments": submission.num_comments
        })

    return posts