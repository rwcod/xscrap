# X Scraper Setup Guide

## Prerequisites

1. MongoDB Installation
- Download and install MongoDB from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
- Start MongoDB service
- Create a new database called `xscraper`

2. Required Python Dependencies
```
playwright
python-dotenv
pymongo
pytest
pytest-asyncio
pytest-mongodb
tqdm
```

## Configuration

1. Environment Variables (.env)
```
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/xscraper

# Scraping Configuration
POSTS_LIMIT=30
HEADLESS=true

# Target Profiles (comma-separated)
TARGET_PROFILES=profile1,profile2,profile3
```

2. Cron Setup

Add the following to your crontab (crontab -e):
```bash
# Run scraper every 6 hours
0 */6 * * * cd /path/to/xscraper && python main.py
```

## Database Schema

### Tweets Collection
```javascript
{
  "_id": ObjectId,        // MongoDB automatic ID
  "tweet_id": String,     // X post ID
  "text": String,        // Post content
  "author_username": String,  // Author's username
  "created_at": DateTime,    // Post creation time
  "scraped_at": DateTime     // When we scraped this post
}

// Indexes:
db.tweets.createIndex({ "tweet_id": 1 }, { unique: true })
```

## Initial Setup Steps

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Configure MongoDB:
```bash
# Start MongoDB service
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS
```

4. Create required indexes:
```bash
# Using mongosh
use xscraper
db.tweets.createIndex({ "tweet_id": 1 }, { unique: true })
```

5. Configure environment variables:
- Copy `.env.example` to `.env`
- Update values as needed

6. Setup cron job:
```bash
crontab -e
# Add the line from Cron Setup section
```

## Monitoring

- Check logs in `xscraper.log`
- Monitor MongoDB using MongoDB Compass
- Check cron execution in system logs