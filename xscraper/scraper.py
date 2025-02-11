import asyncio
from playwright.async_api import async_playwright
import logging
import json
import time
from datetime import datetime
from urllib.parse import urlparse
from .utils import normalize_x_url, extract_username_from_url

logger = logging.getLogger(__name__)

class XScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.base_url = "https://x.com"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    async def init_browser(self):
        """Initialize browser and page"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Wait for network idle to ensure page is fully loaded
        self.page.set_default_navigation_timeout(30000)
        self.page.set_default_timeout(30000)

    async def close(self):
        """Close browser and playwright"""
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def scrape_profile(self, url, max_posts=30):
        """Scrape posts from a profile"""
        try:
            normalized_url = normalize_x_url(url)
            username = extract_username_from_url(normalized_url)
            
            if not username:
                raise ValueError(f"Could not extract username from URL: {url}")
            
            logger.info(f"Starting scrape for user: {username}")
            
            await self.page.goto(normalized_url, wait_until='networkidle')
            await self.page.wait_for_load_state('domcontentloaded')
            
            # Wait for posts to appear
            await self.page.wait_for_selector('article', timeout=10000)
            
            posts = []
            last_height = await self.page.evaluate('document.body.scrollHeight')
            
            while len(posts) < max_posts:
                # Extract posts
                new_posts = await self.extract_posts()
                for post in new_posts:
                    if post not in posts:
                        posts.append(post)
                        if len(posts) >= max_posts:
                            break
                
                # Scroll down
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)  # Wait for content to load
                
                # Check if we've reached the bottom
                new_height = await self.page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height
            
            logger.info(f"Scraped {len(posts)} posts for {username}")
            return posts[:max_posts]
            
        except Exception as e:
            logger.error(f"Error scraping profile {url}: {str(e)}")
            raise

    async def extract_posts(self):
        """Extract posts from current page"""
        posts = []
        articles = await self.page.query_selector_all('article')
        
        for article in articles:
            try:
                post = {}
                
                # Get post time
                time_el = await article.query_selector('time')
                if time_el:
                    post['timestamp'] = await time_el.get_attribute('datetime')
                
                # Get post text
                text_el = await article.query_selector('[data-testid="tweetText"]')
                if text_el:
                    post['text'] = await text_el.text_content()
                else:
                    post['text'] = ""
                
                # Get engagement stats
                stats = await self.extract_post_stats(article)
                post.update(stats)
                
                # Get post URL
                link_el = await article.query_selector('a[href*="/status/"]')
                if link_el:
                    href = await link_el.get_attribute('href')
                    post['url'] = f"https://x.com{href}"
                    post['id'] = href.split('/')[-1]
                
                # Add metadata
                post['scraped_at'] = datetime.utcnow().isoformat()
                
                if 'id' in post:  # Only add posts with valid IDs
                    posts.append(post)
                
            except Exception as e:
                logger.error(f"Error extracting post: {str(e)}")
                continue
        
        return posts

    async def extract_post_stats(self, article):
        """Extract engagement statistics from a post"""
        stats = {
            'replies': 0,
            'reposts': 0,
            'likes': 0,
            'views': 0
        }
        
        try:
            # Find all stat elements
            stat_els = await article.query_selector_all('[data-testid$="count"]')
            
            for el in stat_els:
                test_id = await el.get_attribute('data-testid')
                value = await el.text_content()
                
                # Convert value to number
                try:
                    if 'K' in value:
                        value = float(value.replace('K', '')) * 1000
                    elif 'M' in value:
                        value = float(value.replace('M', '')) * 1000000
                    else:
                        value = int(value or 0)
                except ValueError:
                    value = 0
                
                # Map to correct stat
                if 'reply' in test_id:
                    stats['replies'] = value
                elif 'retweet' in test_id:
                    stats['reposts'] = value
                elif 'like' in test_id:
                    stats['likes'] = value
                elif 'view' in test_id:
                    stats['views'] = value
                
        except Exception as e:
            logger.error(f"Error extracting post stats: {str(e)}")
            
        return stats