import asyncio
import logging
from xscraper.config import Config
from xscraper.auth import BrowserAuth

async def main():
    config = Config.from_env()
    config.setup_logging()
    logger = logging.getLogger(__name__)
    
    async with BrowserAuth(config) as auth:
        try:
            await auth.ensure_authenticated()
            logger.info("Authentication successful")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())