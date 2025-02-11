import re
import logging
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

def normalize_x_url(url):
    """
    Normalize Twitter/X URLs to a standard format
    Examples:
    - https://twitter.com/CounterStrike -> https://x.com/CounterStrike
    - https://x.com/CounterStrike -> https://x.com/CounterStrike
    - @CounterStrike -> https://x.com/CounterStrike
    - CounterStrike -> https://x.com/CounterStrike
    """
    try:
        # Remove any whitespace
        url = url.strip()
        
        # If it's just a handle (with or without @)
        if not url.startswith(('http://', 'https://')):
            handle = url.lstrip('@')
            return f'https://x.com/{handle}'
        
        # Parse the URL
        parsed = urlparse(url)
        
        # Convert twitter.com to x.com
        if parsed.netloc == 'twitter.com':
            parsed = parsed._replace(netloc='x.com')
        
        # Ensure it's using https
        parsed = parsed._replace(scheme='https')
        
        # Rebuild the URL with only the essential parts
        path = parsed.path.rstrip('/')  # Remove trailing slashes
        normalized = f'https://{parsed.netloc}{path}'
        
        logger.debug(f"Normalized URL: {url} -> {normalized}")
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing URL {url}: {str(e)}")
        return url

def extract_username_from_url(url):
    """Extract username from Twitter/X URL"""
    try:
        normalized = normalize_x_url(url)
        username = normalized.split('/')[-1]
        return username
    except Exception as e:
        logger.error(f"Error extracting username from URL {url}: {str(e)}")
        return None

def is_valid_x_url(url):
    """Check if the URL is a valid Twitter/X profile URL"""
    try:
        normalized = normalize_x_url(url)
        parsed = urlparse(normalized)
        
        # Check basic URL structure
        if parsed.netloc not in ['x.com', 'twitter.com']:
            return False
            
        # Extract username
        username = extract_username_from_url(normalized)
        
        # Basic username validation
        if not username or not re.match(r'^[A-Za-z0-9_]{1,15}$', username):
            return False
            
        return True
    except Exception:
        return False