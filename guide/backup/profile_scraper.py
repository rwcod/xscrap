import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup

class ProfileScraper:
    def __init__(self, db_handler, browser, profile_queue, min_followers):
        self.db = db_handler
        self.browser = browser
        self.profile_queue = profile_queue
        self.min_followers = min_followers
        self.browser = None
        self.page = None

    async def start(self):
        """Initialize browser and page"""
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({'width': 1280, 'height': 800})

    async def process_profiles(self):
        """Process profiles from queue in real-time"""
        # Get and validate profile URLs
        profile_urls = self.db.get_profile_urls()
        if not profile_urls:
            print("No profile URLs found in database")
            return
            
        print(f"Found {len(profile_urls)} profiles to scrape")
        
        for url in profile_urls:
            print(f"Scraping: {url}")
            try:
                await self.page.goto(url, {'waitUntil': 'networkidle2'})
                await self._scrape_profile_data()
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
        
        # Wait for profile to load
        await self.page.waitForSelector('div[data-testid="UserProfileHeader_Items"]')
        
        # Get page content
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract profile data
        profile_data = {}
        
        # Get username
        username_div = soup.find('div', {'data-testid': 'UserProfileHeader_Items'})
        if username_div:
            profile_data['username'] = username_div.find('span').text.strip()
            
            # Get follower counts
            followers_div = soup.find('a', href=lambda x: x and 'followers' in x)
            if followers_div:
                profile_data['followers'] = int(''.join(filter(str.isdigit, followers_div.text)) or 0)
                
            # Get following count
            following_div = soup.find('a', href=lambda x: x and 'following' in x)
            if following_div:
                profile_data['following'] = int(''.join(filter(str.isdigit, following_div.text)) or 0)
                
            # Check if verified
            verified_icon = soup.find('svg', {'aria-label': 'Verified account'})
            profile_data['verified'] = verified_icon is not None
            
            # Save profile data
            self.db.add_profile(profile_data)

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()