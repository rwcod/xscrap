import asyncio
import logging
from xscraper.scraper import XScraper

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_scrape():
    """Test scraping a single profile"""
    try:
        # Test profile URL
        url = "https://x.com/CounterStrike"
        
        logger.info(f"Testing scraper with profile: {url}")
        
        # Initialize scraper (using headless mode)
        scraper = XScraper(headless=True)
        await scraper.init_browser()
        
        try:
            # Scrape posts
            posts = await scraper.scrape_profile(url, max_posts=5)
            
            # Print results
            logger.info(f"Found {len(posts)} posts")
            
            for post in posts:
                logger.info("-" * 80)
                logger.info(f"Post ID: {post.get('id')}")
                logger.info(f"Timestamp: {post.get('timestamp')}")
                logger.info(f"Text: {post.get('text')[:200]}..." if post.get('text') else "No text")
                logger.info(f"Likes: {post.get('likes')}")
                logger.info(f"Reposts: {post.get('reposts')}")
                logger.info(f"Replies: {post.get('replies')}")
                logger.info(f"Views: {post.get('views')}")
                logger.info(f"URL: {post.get('url')}")
                
        finally:
            await scraper.close()
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        logger.error(f"Browser logs:\n{e}")

if __name__ == "__main__":
    logger.info("Starting scraper test")
    asyncio.run(test_scrape())
    logger.info("Test completed")