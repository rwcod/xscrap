#!/usr/bin/env python3
"""
Utility script to manage and view scraped data in MongoDB.
Can be run inside Docker container: docker-compose exec scraper python scripts/manage_data.py
"""

import argparse
from datetime import datetime, timedelta
import json
import sys
import os

from pymongo import MongoClient
from tabulate import tabulate
from bson import json_util

def connect_mongodb():
    """Connect to MongoDB"""
    uri = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017/xscraper')
    client = MongoClient(uri)
    return client.xscraper

def format_tweet(tweet):
    """Format tweet for display"""
    return {
        'author': tweet['author_username'],
        'text': tweet['text'][:100] + '...' if len(tweet['text']) > 100 else tweet['text'],
        'created_at': tweet['created_at'].strftime('%Y-%m-%d %H:%M'),
        'scraped_at': tweet['scraped_at'].strftime('%Y-%m-%d %H:%M')
    }

def list_recent_tweets(db, limit=10):
    """List most recent tweets"""
    tweets = db.tweets.find().sort('created_at', -1).limit(limit)
    formatted = [format_tweet(t) for t in tweets]
    print("\nMost Recent Tweets:")
    print(tabulate(formatted, headers='keys', tablefmt='grid'))

def show_stats(db):
    """Show collection statistics"""
    total_tweets = db.tweets.count_documents({})
    total_authors = len(db.tweets.distinct('author_username'))
    
    # Get stats for last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    new_tweets = db.tweets.count_documents({'scraped_at': {'$gte': yesterday}})
    
    print("\nCollection Statistics:")
    print(f"Total Tweets: {total_tweets}")
    print(f"Total Authors: {total_authors}")
    print(f"New Tweets (24h): {new_tweets}")
    
    # Show tweets per author
    print("\nTweets per Author:")
    pipeline = [
        {'$group': {'_id': '$author_username', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    author_stats = list(db.tweets.aggregate(pipeline))
    print(tabulate(author_stats, headers=['Author', 'Tweets'], tablefmt='grid'))

def export_data(db, output_file):
    """Export tweets to JSON file"""
    tweets = list(db.tweets.find())
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tweets, f, default=json_util.default, indent=2, ensure_ascii=False)
    print(f"\nData exported to {output_file}")

def clean_old_tweets(db, days):
    """Remove tweets older than specified days"""
    cutoff = datetime.now() - timedelta(days=days)
    result = db.tweets.delete_many({'created_at': {'$lt': cutoff}})
    print(f"\nRemoved {result.deleted_count} tweets older than {days} days")

def main():
    parser = argparse.ArgumentParser(description="Manage X scraper data")
    parser.add_argument('--list', '-l', type=int, metavar='N',
                       help='List N most recent tweets')
    parser.add_argument('--stats', '-s', action='store_true',
                       help='Show collection statistics')
    parser.add_argument('--export', '-e', metavar='FILE',
                       help='Export tweets to JSON file')
    parser.add_argument('--clean', '-c', type=int, metavar='DAYS',
                       help='Remove tweets older than DAYS days')
    
    args = parser.parse_args()
    
    try:
        db = connect_mongodb()
        
        if args.list:
            list_recent_tweets(db, args.list)
        if args.stats:
            show_stats(db)
        if args.export:
            export_data(db, args.export)
        if args.clean:
            clean_old_tweets(db, args.clean)
            
        if not any(vars(args).values()):
            # If no arguments provided, show help
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()