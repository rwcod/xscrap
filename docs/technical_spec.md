# X Scraper Technical Specification

## System Architecture

### Components

1. **MongoDB Integration (`db_manager.py`)**
```python
class DBManager:
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client.xscraper
        self.tweets = self.db.tweets

    async def save_tweet(self, tweet: Tweet) -> bool:
        # Handles deduplication via unique index
        try:
            self.tweets.insert_one({
                "tweet_id": tweet.id,
                "text": tweet.text,
                "author_username": tweet.author_username,
                "created_at": tweet.created_at,
                "scraped_at": datetime.now()
            })
            return True
        except DuplicateKeyError:
            return False
```

2. **Tweet Model (`models.py`)**
```python
@dataclass
class Tweet:
    id: str
    text: str
    created_at: datetime
    author_username: str
```

3. **Scraper (`scraper.py`)**
```python
class Scraper:
    def __init__(self, config: Config, db_manager: DBManager):
        self.config = config
        self.db = db_manager
        self.auth = None
        
    async def scrape_profile(self, username: str) -> list[Tweet]:
        """Scrape last N posts from a profile"""
        posts = []
        try:
            # Navigate to profile
            await self.page.goto(f"{self.config.base_url}/{username}")
            await self.page.wait_for_selector('article')
            
            # Get specified number of posts
            while len(posts) < self.config.posts_limit:
                new_posts = await self._extract_tweets()
                posts.extend(new_posts)
                await self.page.evaluate('window.scrollBy(0, 1000)')
                await self.page.wait_for_timeout(1000)
                
            return posts[:self.config.posts_limit]
        except Exception as e:
            self.logger.error(f"Error scraping profile {username}: {e}")
            return []
```

4. **Configuration (`config.py`)**
```python
@dataclass
class Config:
    mongodb_uri: str
    posts_limit: int = 30
    headless: bool = True
    target_profiles: list[str] = field(default_factory=list)
    base_url: str = "https://twitter.com"
    
    @classmethod
    def from_env(cls) -> 'Config':
        load_dotenv()
        return cls(
            mongodb_uri=os.getenv('MONGODB_URI'),
            posts_limit=int(os.getenv('POSTS_LIMIT', '30')),
            headless=os.getenv('HEADLESS', 'true').lower() == 'true',
            target_profiles=os.getenv('TARGET_PROFILES', '').split(',')
        )
```

5. **Main Script (`main.py`)**
```python
async def main():
    config = Config.from_env()
    db_manager = DBManager(config.mongodb_uri)
    
    async with Scraper(config, db_manager) as scraper:
        for profile in config.target_profiles:
            tweets = await scraper.scrape_profile(profile)
            for tweet in tweets:
                await db_manager.save_tweet(tweet)

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

1. **Network Issues**
- Implement exponential backoff for retries
- Log failed attempts
- Continue with next profile if one fails

2. **Rate Limiting**
- Respect X's rate limits
- Add delays between requests
- Track rate limit headers

3. **Database Errors**
- Handle connection issues
- Implement reconnection logic
- Log failed saves

## Monitoring

1. **Logging**
- Profile scraping status
- Database operations
- Rate limit warnings
- Error conditions

2. **Metrics**
- Number of posts scraped
- Number of new vs duplicate posts
- Processing time per profile
- Success/failure rates

## Testing Strategy

1. **Unit Tests**
- Mock MongoDB operations
- Test tweet extraction logic
- Validate configuration loading

2. **Integration Tests**
- Test database operations
- Verify deduplication
- Test profile scraping

3. **End-to-End Tests**
- Complete scraping workflow
- Database integration
- Cron execution

## Security Considerations

1. **Data Storage**
- Secure MongoDB connection
- No sensitive data storage
- Regular backup strategy

2. **Authentication**
- Secure storage of X session
- Rotate credentials if needed
- Monitor auth failures

## Performance Optimization

1. **Database**
- Proper indexing
- Bulk operations where possible
- Connection pooling

2. **Scraping**
- Optimal scroll timing
- Memory usage monitoring
- Resource cleanup

## Deployment

1. **Dependencies**
- Version pinning
- Virtual environment
- Playwright requirements

2. **Cron Setup**
- Logging configuration
- Error notification
- Resource limits

3. **Monitoring**
- Log rotation
- Disk space monitoring
- Process monitoring