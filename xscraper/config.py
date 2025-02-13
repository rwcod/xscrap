from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
import os
import logging

@dataclass
class Config:
    """Configuration for X scraper"""
    
    # MongoDB settings
    mongodb_uri: str
    
    # Scraping settings
    posts_limit: int = 30
    headless: bool = True
    
    # Browser settings
    timeout: int = 45000  # milliseconds
    base_url: str = "https://twitter.com"
    login_url: str = "https://twitter.com/login"
    cookies_path: str = "auth.json"
    viewport_width: int = 1280
    viewport_height: int = 720
    
    # Logging
    log_level: str = 'INFO'
    
    @classmethod
    def from_env(cls, env_path: str = '.env') -> 'Config':
        """Create configuration from environment variables"""
        load_dotenv(env_path)
        
        # Get required MongoDB URI
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is required")
            
        return cls(
            mongodb_uri=mongodb_uri,
            posts_limit=int(os.getenv('POSTS_LIMIT', '30')),
            headless=os.getenv('HEADLESS', 'true').lower() == 'true',
            timeout=int(os.getenv('TIMEOUT', '45000')),
            viewport_width=int(os.getenv('VIEWPORT_WIDTH', '1280')),
            viewport_height=int(os.getenv('VIEWPORT_HEIGHT', '720')),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
        
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='xscraper.log'
        )