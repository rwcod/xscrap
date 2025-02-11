import asyncio
from xscraper.config import Config
from xscraper.scraper import Scraper

async def main():
    # 1. Get config from GUI
    config = Config.from_gui()
    
    # 2. Start scraping
    async with Scraper(config) as scraper:
        results = await scraper.search(config.target_keyword)
        print(f"Found {len(results)} results")

if __name__ == "__main__":
    asyncio.run(main())
