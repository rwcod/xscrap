import asyncio
import os
import time
from xscraper.config import Config
from xscraper.auth import BrowserAuth

async def auth_test_flow():
    # Clean previous session
    if os.path.exists('auth.json'):
        os.remove('auth.json')
    
    config = Config.from_env_file()
    config.headless = False  # Override headless setting
    
    # Test first-run authentication
    print("\n=== First Run: Manual Login Test ===")
    async with BrowserAuth(config) as auth:
        result = await auth.ensure_authenticated()
        assert result is True, "First login failed"
        print("First login successful")
    
    # Test subsequent auto-login
    print("\n=== Second Run: Cookie Login Test ===")
    async with BrowserAuth(config) as auth:
        result = await auth.ensure_authenticated()
        assert result is True, "Cookie login failed"
        print("Auto-login successful")
    
    # Test invalid cookie recovery
    print("\n=== Third Run: Invalid Cookie Test ===")
    with open('auth.json', 'w') as f:
        f.write("invalid cookies")
    
    async with BrowserAuth(config) as auth:
        result = await auth.ensure_authenticated()
        assert result is True, "Invalid cookie recovery failed"
        print("Cookie refresh successful")

async def verify_cookie_usage():
    config = Config.from_env_file()
    config.headless = False
    
    print("\n=== Cookie Verification Test ===")
    
    # Ensure auth.json exists
    if not os.path.exists('auth.json'):
        print("Error: Run initial login test first")
        return
    
    async with BrowserAuth(config) as auth:
        start_time = time.time()
        result = await auth.ensure_authenticated()
        duration = time.time() - start_time
        
        assert result is True, "Authentication failed with valid cookies"
        assert duration < 3, "Cookie check took too long"
        print(f"Verified cookies in {duration:.1f}s")
        await auth.page.screenshot(path='cookie_check.png')

if __name__ == '__main__':
    asyncio.run(auth_test_flow())
    asyncio.run(verify_cookie_usage())
    print("\nAll authentication tests passed!") 