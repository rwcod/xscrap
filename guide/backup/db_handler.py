import sqlite3
import json
from datetime import datetime

class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect('tweets.db')
        self._init_db()
        
    def _init_db(self):
        c = self.conn.cursor()
        
        # Create tweets table with proper comma separation
        c.execute('''CREATE TABLE IF NOT EXISTS tweets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            profile_url TEXT NOT NULL,
            tweet_id TEXT,
            content TEXT,
            likes INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            hashtags TEXT,
            cashtags TEXT,
            hashtag_count INTEGER DEFAULT 0,
            cashtag_count INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(profile_url, tweet_id)
        )''')
        
        # Create profile cache table
        c.execute('''CREATE TABLE IF NOT EXISTS profile_cache(
            profile_url TEXT PRIMARY KEY,
            followers INTEGER,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        self.conn.commit()

    def add_tweet(self, tweet_data):
        c = self.conn.cursor()
        try:
            c.execute('''INSERT OR IGNORE INTO tweets 
                (username, profile_url, tweet_id, content, likes, retweets, 
                 replies, views, hashtags, cashtags, hashtag_count, cashtag_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    tweet_data['username'],
                    tweet_data['profile_url'],
                    tweet_data.get('tweet_id', ''),
                    tweet_data.get('content', ''),
                    tweet_data.get('likes', 0),
                    tweet_data.get('retweets', 0),
                    tweet_data.get('replies', 0),
                    tweet_data.get('views', 0),
                    ','.join(tweet_data.get('hashtags', [])),
                    ','.join(tweet_data.get('cashtags', [])),
                    len(tweet_data.get('hashtags', [])),
                    len(tweet_data.get('cashtags', []))
                ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_profile_urls(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT profile_url FROM tweets")
        return [row[0] for row in c.fetchall()]

    def export_to_json(self):
        c = self.conn.cursor()
        c.execute('''SELECT t.*, p.followers 
                   FROM tweets t
                   LEFT JOIN profile_cache p ON t.profile_url = p.profile_url''')
        
        columns = [desc[0] for desc in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        with open('output.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

    def __del__(self):
        if self.conn:
            self.conn.close()