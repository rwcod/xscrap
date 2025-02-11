import os
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from .config import Config

class BrowserAuth:
    MAX_RETRIES = 3
    RETRY_DELAY = 5

    def __init__(self, config: Config, headless=False):
        self.config = config
        self.headless = headless
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.cookie_path = 'auth.json'
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        await self.launch_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def launch_browser(self):
        self.logger.info("Launching browser...")
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless
            )
            
            self.context = await self.browser.new_context(
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                }
            )
            
            self.page = await self.context.new_page()
            self.logger.info("Browser launched successfully")
            
            if os.path.exists(self.cookie_path):
                with open(self.cookie_path) as f:
                    cookies = json.load(f)
                    await self.context.add_cookies(cookies)
            
        except Exception as e:
            self.logger.error(f"Failed to launch browser: {str(e)}")
            raise

    async def ensure_authenticated(self) -> bool:
        for attempt in range(self.MAX_RETRIES):
            try:
                if await self._has_valid_cookies():
                    return True
                    
                if attempt < self.MAX_RETRIES - 1:
                    await self.manual_login()
                    if await self._has_valid_cookies():
                        return True
                        
                await asyncio.sleep(self.RETRY_DELAY)
                
            except Exception as e:
                self.logger.error(f"Authentication attempt {attempt + 1} failed: {e}")
                
        raise AuthenticationError("Failed to authenticate after multiple attempts")

    async def check_auth(self):
        try:
            await self.page.goto(self.config.base_url)
            # Check if login button exists
            login_button = await self.page.query_selector('a[href="/login"]')
            return login_button is None
        except Exception as e:
            print(f"Error checking auth: {e}")
            return False

    async def manual_login(self):
        await self.page.goto(self.config.login_url)
        print("Please login manually in the browser window")
        print("Waiting for navigation to complete...")
        await self.page.wait_for_url(self.config.base_url, timeout=60000)
        await self.save_cookies()
        return True

    async def save_cookies(self):
        cookies = await self.context.cookies()
        with open(self.config.cookies_path, 'w') as f:
            json.dump(cookies, f)

    async def load_cookies(self):
        try:
            with open(self.config.cookies_path, 'r') as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
        except Exception as e:
            print(f"Error loading cookies: {e}")

    async def close(self):
        if self.page:
            cookies = await self.context.cookies()
            with open(self.cookie_path, 'w') as f:
                json.dump(cookies, f)
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def _has_valid_cookies(self):
        """Check cookies using the main browser context"""
        try:
            # Load cookies into main context
            if not os.path.exists(self.cookie_path):
                self.logger.debug("No cookies file")
                return False
            
            self.context = await self.browser.new_context(
                storage_state=self.cookie_path,
                viewport={'width': 1280, 'height': 720}
            )
            
            # Check login state
            if not self.page:
                self.page = await self.context.new_page()
                
            await self.page.goto('https://x.com', wait_until='networkidle')
            logged_in = await self.page.query_selector('text=Home') is not None
            self.logger.debug(f"Cookies valid: {logged_in}")
            return logged_in
        
        except Exception as e:
            self.logger.error(f"Cookie check failed: {str(e)}")
            return False

print("Tkinter version:", tk.TkVersion)  # Should be >=8.6