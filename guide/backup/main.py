import asyncio
import json
import os
import subprocess
from pyppeteer import launch, errors
from input_handler import InputHandler
from db_handler import DataStorageHandler
from tweet_scraper import TweetScraper
from profile_scraper import ProfileScraper

async def main():
    try:
        # Initialize core components
        input_handler = InputHandler()
        params = input_handler.get_parameters()
        input_handler.save_parameters(params)
        db_handler = DataStorageHandler(output_format=params['output_format'])

        # Configure browser with Windows-specific settings
        browser = await launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list'
            ],
            executablePath=params['chrome_path'],
            ignoreHTTPSErrors=True,
            userDataDir=os.path.join(os.getcwd(), 'user_data'),
            defaultViewport={'width': 1280, 'height': 800}
        )

        # Create isolated browser contexts
        tweet_context = await browser.createIncognitoBrowserContext()
        profile_context = await browser.createIncognitoBrowserContext()
        profile_queue = asyncio.Queue()

        # Handle browser session
        page = await browser.newPage()
        session_file = 'x_session.json'
        
        if os.path.exists(session_file):
            print("Loading existing session...")
            with open(session_file, 'r') as f:
                cookies = json.load(f)
            await page.setCookie(*cookies)
            await page.goto('https://x.com/home')
        else:
            print("Please complete login within 2 minutes...")
            await page.goto('https://x.com/login')
        
        try:
            await page.waitForSelector('div[data-testid="User-Name"]', {'timeout': 120000})
            print("Login successful! Saving session...")
            cookies = await page.cookies()
            with open(session_file, 'w') as f:
                json.dump(cookies, f)
        except errors.TimeoutError:
            print("Login timed out. Please try again.")
            await browser.close()
            return

        # Initialize scrapers with parameters
        tweet_scraper = TweetScraper(
            db_handler=db_handler,
            browser=browser,
            profile_queue=profile_queue
        )
        profile_scraper = ProfileScraper(
            db_handler=db_handler,
            browser=browser,
            profile_queue=profile_queue
        )

        # Run scrapers concurrently
        await asyncio.gather(
            tweet_scraper.scrape(params['keyword']),
            profile_scraper.process_profiles()
        )

    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        if 'browser' in locals():
            await browser.close()
        if os.path.exists('x_session.json'):
            os.remove('x_session.json')
        db_handler.export_to_json()
        print("Operation completed successfully. Results saved to output.json")

if __name__ == "__main__":
    asyncio.run(main())