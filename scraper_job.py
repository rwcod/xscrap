import asyncio
import logging
import os
from datetime import datetime
from pymongo import MongoClient
from xscraper.scraper import XScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)

# MongoDB settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/xscraper")
POSTS_LIMIT = int(os.getenv("POSTS_LIMIT", "30"))
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

async def scrape_and_store(profile_url, database_id, profile_id, mongo_client):
    """Scrape a profile and store results in MongoDB"""
    try:
        # Initialize scraper
        scraper = XScraper(headless=HEADLESS)
        await scraper.init_browser()
        
        try:
            # Scrape posts
            posts = await scraper.scrape_profile(profile_url, POSTS_LIMIT)
            logger.info(f"Scraped {len(posts)} posts from {profile_url}")
            
            if posts:
                db = mongo_client.get_database()
                
                # Store each post
                for post in posts:
                    # Add metadata
                    post['database_id'] = database_id
                    post['profile_id'] = profile_id
                    post['profile_url'] = profile_url
                    post['last_updated'] = datetime.utcnow()
                    
                    # Update or insert post
                    db.scraped_data.update_one(
                        {
                            'database_id': database_id,
                            'profile_id': profile_id,
                            'id': post['id']
                        },
                        {'$set': post},
                        upsert=True
                    )
                
                # Update profile's last scraped time
                db.profiles.update_one(
                    {'_id': profile_id},
                    {
                        '$set': {
                            'last_scraped': datetime.utcnow(),
                            'last_scrape_count': len(posts)
                        }
                    }
                )
                
                # Update database's last updated time
                db.game_databases.update_one(
                    {'_id': database_id},
                    {'$set': {'last_updated': datetime.utcnow()}}
                )
                
                return len(posts)
            
            return 0
            
        finally:
            await scraper.close()
            
    except Exception as e:
        logger.error(f"Error scraping {profile_url}: {str(e)}")
        return 0

async def scrape_all_profiles():
    """Scrape all active profiles"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        
        # Get all active profiles
        profiles = list(db.profiles.find({'active': True}))
        logger.info(f"Found {len(profiles)} active profiles to scrape")
        
        total_posts = 0
        for profile in profiles:
            try:
                posts_count = await scrape_and_store(
                    profile['url'],
                    profile['database_id'],
                    profile['_id'],
                    client
                )
                total_posts += posts_count
                
                # Wait between profiles
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing profile {profile['url']}: {str(e)}")
                continue
                
        logger.info(f"Scraping completed. Total posts scraped: {total_posts}")
        
    except Exception as e:
        logger.error(f"Scraping job error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    logger.info("Starting scraping job")
    asyncio.run(scrape_all_profiles())
    logger.info("Scraping job completed")