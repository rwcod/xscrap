import os
import asyncio
from playwright.async_api import async_playwright
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox

class BrowserAuth:
    def __init__(self, config):
        self.config = config
        self.browser = None
        self.context = None
        self.page = None
        self.cookie_path = 'auth.json'
        self.logger = logging.getLogger('auth')

    async def __aenter__(self):
        await self.launch_browser()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def launch_browser(self):
        self.logger.debug("Initializing browser context")
        has_cookies = await self._has_valid_cookies()
        self.logger.debug(f"Has cookies: {has_cookies}")
        
        if self.config.dev_mode:
            headless = False
        else:
            headless = has_cookies
        
        self.logger.debug(f"Launching {'dev' if self.config.dev_mode else 'prod'} browser (headless={headless})")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox']
        )
        
        # Log browser version
        self.logger.debug(f"Browser version: {self.browser.version}")
        
        # Load cookies if valid
        if not self.config.dev_mode and await self._has_valid_cookies():
            self.context = await self.browser.new_context(
                storage_state=self.cookie_path,
                viewport={'width': 1280, 'height': 720}
            )
        else:
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
        
        self.page = await self.context.new_page()
        self.logger.debug(f"Browser launched (headless={headless})")

    async def ensure_authenticated(self):
        # Check current auth state
        await self.page.goto('https://x.com', wait_until='networkidle')
        
        # Check for logged-in element
        try:
            await self.page.wait_for_selector('[data-testid="AppTabBar_Home_Link"]', timeout=5000)
            self.logger.info("Already authenticated")
            return True
        except:
            self.logger.warning("Session expired, re-authenticating")
        
        # Manual login
        await self.page.goto('https://x.com/i/flow/login')
        self.logger.info("Please login in the browser...")
        
        # Wait for home page
        try:
            await self.page.wait_for_selector('[data-testid="AppTabBar_Home_Link"]', timeout=0)
            await self.context.storage_state(path=self.cookie_path)
            self.logger.info("Login successful")
            return True
        except:
            self.logger.error("Login failed")
            return False

    async def _is_logged_in(self):
        """Check for presence of compose tweet button"""
        try:
            await self.page.wait_for_selector('[data-testid="tweetButton"]', timeout=10000)
            self.logger.debug("Login verified via tweet button")
            return True
        except Exception as e:
            self.logger.debug(f"Not logged in: {str(e)}")
            return False

    async def _perform_manual_login(self):
        print("Please log in through the browser...")
        await self.page.goto('https://x.com/login')
        
        # Wait for manual login completion
        try:
            await self.page.wait_for_url('**://x.com/home', timeout=0)
            await self.context.storage_state(path=self.cookie_path)
            print("Authentication successful, cookies saved")
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def _has_valid_cookies(self):
        """Check cookies using the main browser context"""
        if not os.path.exists(self.cookie_path):
            self.logger.debug("No cookies file")
            return False
        
        try:
            # Load cookies into main context
            self.context = await self.browser.new_context(
                storage_state=self.cookie_path,
                viewport={'width': 1280, 'height': 720}
            )
            self.page = await self.context.new_page()
            
            # Check login state
            await self.page.goto('https://x.com', wait_until='networkidle')
            logged_in = await self.page.query_selector('text=Home') is not None
            self.logger.debug(f"Cookies valid: {logged_in}")
            return logged_in
            
        except Exception as e:
            self.logger.error(f"Cookie check failed: {str(e)}")
            return False

print("Tkinter version:", tk.TkVersion)  # Should be >=8.6 