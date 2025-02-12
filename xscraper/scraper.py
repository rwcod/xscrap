from datetime import datetime
import logging
import asyncio
from typing import List, Optional

from .models import Tweet
from .auth import BrowserAuth
from .db_manager import DBManager

class Scraper:
    """Scrapes posts from X (Twitter) profiles"""
    
    def __init__(self, config, db_manager: DBManager):
        self.config = config
        self.db = db_manager
        self.auth = None
        self.logger = logging.getLogger(__name__)
        self.rate_limit_delay = 1.0  # seconds between requests
        
    async def __aenter__(self):
        """Setup browser and authentication"""
        self.auth = BrowserAuth(headless=self.config.headless)
        await self.auth.__aenter__()
        return self
        
    async def __aexit__(self, *args):
        """Cleanup browser resources"""
        await self.auth.__aexit__(*args)
        
    async def _respect_rate_limit(self):
        """Implement rate limiting between requests"""
        await asyncio.sleep(self.rate_limit_delay)
        
    async def scrape_profile(self, username: str) -> List[Tweet]:
        """Scrape recent posts from a profile"""
        await self._respect_rate_limit()
        posts = []
        page = self.auth.page
        
        try:
            # Navigate to profile
            await page.goto(f"{self.config.base_url}/{username}")
            await page.wait_for_selector('[data-testid="primaryColumn"]')
            
            # Scroll and collect posts until we have enough
            while len(posts) < self.config.posts_limit:
                new_posts = await self._extract_tweets()
                posts.extend(new_posts)
                
                # Break if we got enough posts
                if len(posts) >= self.config.posts_limit:
                    break
                    
                # Scroll for more posts
                await page.evaluate('window.scrollBy(0, 1000)')
                await page.wait_for_timeout(1000)
                
            # Return only the requested number of posts
            return posts[:self.config.posts_limit]
            
        except Exception as e:
            self.logger.error(f"Error scraping profile {username}: {e}")
            return []
            
    async def _extract_tweets(self) -> List[Tweet]:
        """Extract tweets from current page"""
        tweets = []
        elements = await self.auth.page.query_selector_all('article[data-testid="tweet"]')
        
    async def _extract_tweets(self):
        tweets = []
        elements = await self.page.query_selector_all('article')
        for element in elements:
            tweet_text = await element.evaluate('el => el.textContent')
            tweets.append(tweet_text)
        return tweets