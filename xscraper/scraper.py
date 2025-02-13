from datetime import datetime
import logging
import asyncio
from typing import List, Optional

from .models import Tweet
from .auth import BrowserAuth
from .db_manager import DBManager
from .config import Config

class XScraper:
    """Scrapes posts from X (Twitter) profiles"""
    
    def __init__(self, headless=True):
        self.config = Config.from_env()  # Use from_env instead of direct instantiation
        self.config.headless = headless  # Override headless setting if provided
        self.auth = None
        self.logger = logging.getLogger(__name__)
        self.rate_limit_delay = 1.0  # seconds between requests
        
    async def init_browser(self):
        """Initialize browser with authentication"""
        self.auth = BrowserAuth(self.config, headless=self.config.headless)
        await self.auth.__aenter__()
        return self
        
    async def close(self):
        """Close browser and cleanup resources"""
        if self.auth:
            await self.auth.__aexit__(None, None, None)
        
    async def _respect_rate_limit(self):
        """Implement rate limiting between requests"""
        await asyncio.sleep(self.rate_limit_delay)
        
    async def scrape_profile(self, profile_url: str, max_posts: int = 30) -> List[dict]:
        """Scrape recent posts from a profile"""
        await self._respect_rate_limit()
        posts = []
        page = self.auth.page
        
        try:
            # Navigate to profile
            await page.goto(profile_url)
            await page.wait_for_selector('[data-testid="primaryColumn"]')
            
            # Scroll and collect posts until we have enough
            while len(posts) < max_posts:
                new_posts = await self._extract_tweets()
                posts.extend(new_posts)
                
                # Break if we got enough posts
                if len(posts) >= max_posts:
                    break
                    
                # Scroll for more posts
                await page.evaluate('window.scrollBy(0, 1000)')
                await page.wait_for_timeout(1000)
                
            # Convert to dictionary format expected by web app
            formatted_posts = []
            for post in posts[:max_posts]:
                formatted_posts.append({
                    'id': str(post['id']),
                    'text': post['text'],
                    'timestamp': post['created_at'].isoformat() + 'Z',
                    'url': f"{profile_url}/status/{post['id']}"
                })
                
            return formatted_posts
            
        except Exception as e:
            self.logger.error(f"Error scraping profile {profile_url}: {e}")
            return []
            
    async def _extract_tweets(self) -> List[dict]:
        """Extract tweets from current page"""
        tweets = []
        elements = await self.auth.page.query_selector_all('article[data-testid="tweet"]')
        
        for element in elements:
            try:
                # Get tweet ID from article
                tweet_link = await element.query_selector('a[href*="/status/"]')
                if not tweet_link:
                    continue
                    
                href = await tweet_link.get_attribute('href')
                tweet_id = href.split('/status/')[1].split('?')[0]
                
                # Get tweet text
                text_element = await element.query_selector('[data-testid="tweetText"]')
                text = await text_element.text_content() if text_element else ""
                
                # Get timestamp
                time_element = await element.query_selector('time')
                timestamp = await time_element.get_attribute('datetime') if time_element else None
                created_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.utcnow()
                
                tweets.append({
                    'id': tweet_id,
                    'text': text,
                    'created_at': created_at
                })
                
            except Exception as e:
                self.logger.error(f"Error extracting tweet: {e}")
                continue
                
        return tweets