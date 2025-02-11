#!/usr/bin/env python3
"""
Test script to verify Docker setup is working correctly.
Tests MongoDB connection and scraper functionality.
"""

import asyncio
import logging
from datetime import datetime
import os
import sys

from pymongo import MongoClient
from pymongo.errors import ConnectionError

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xscraper.config import Config
from xscraper.db_manager import DBManager
from xscraper.scraper import Scraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_mongodb():
    """Test MongoDB connection"""
    logger.info("Testing MongoDB connection...")
    
    uri = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017/xscraper')
    try:
        client = MongoClient(uri)
        db = client.xscraper
        
        # Test connection
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        
        # Test write
        test_doc = {
            "test_id": f"test_{datetime.now().isoformat()}",
            "timestamp": datetime.now()
        }
        db.test_collection.insert_one(test_doc)
        logger.info("✓ MongoDB write test successful")
        
        # Clean up
        db.test_collection.delete_one({"test_id": test_doc["test_id"]})
        client.close()
        return True
        
    except ConnectionError as e:
        logger.error(f"MongoDB connection error: {e}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error during MongoDB test: {e}")
        return False

async def test_scraper():
    """Test scraper functionality"""
    logger.info("Testing scraper setup...")
    
    try:
        config = Config.from_env()
        db_manager = DBManager(config.mongodb_uri)
        
        if not db_manager.connect():
            logger.error("Failed to connect to MongoDB")
            return False
            
        # Test with a single public profile
        test_profile = "Twitter"  # Official Twitter account as test
        
        async with Scraper(config, db_manager) as scraper:
            tweets = await scraper.scrape_profile(test_profile)
            
            if not tweets:
                logger.error("No tweets retrieved")
                return False
                
            logger.info(f"✓ Successfully retrieved {len(tweets)} tweets")
            
            # Try saving to MongoDB
            saved, duplicates = await db_manager.save_tweets(tweets)
            logger.info(f"✓ Saved {saved} tweets, {duplicates} duplicates skipped")
            
        return True
        
    except Exception as e:
        logger.error(f"Error during scraper test: {e}")
        return False
        
    finally:
        if db_manager:
            db_manager.close()

async def main():
    """Run all tests"""
    logger.info("Starting Docker setup tests...")
    
    # Test MongoDB
    if not await test_mongodb():
        logger.error("MongoDB test failed")
        return False
        
    # Test Scraper
    if not await test_scraper():
        logger.error("Scraper test failed")
        return False
        
    logger.info("✓ All tests passed successfully!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)