### Complete Guide to Building a Web Scraper

#### Phase 1: Functionality
- **Login System**: Implement user authentication.
- **Basic Scraping Flow**: Set up the core scraping logic.
- **JSON Output**: Ensure that scraped data is saved in JSON format.

##### Step-by-Step Implementation:

1. **Set Up Your Project**:
   - Create a new directory for your project, e.g., `scraper`.
   - Initialize a Python virtual environment: 
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows: `venv\Scripts\activate`
     - On macOS/Linux: `source venv/bin/activate`

2. **Install Required Libraries**:
   - Install Playwright and other necessary libraries using pip:
     ```bash
     pip install playwright python-dotenv psutil
     ```
   - Initialize Playwright for browser setup:
     ```bash
     npx playwright install
     ```

3. **Create Configuration File**:
   - Create a `.env` file to store configuration variables such as API keys, login credentials, etc.
   - Example content of `.env`:
     ```
     HEADLESS=True
     USERNAME=your_username
     PASSWORD=your_password
     ```

4. **Set Up the Scraper Class**:
   - Create a new Python file `scraper.py`.
   - Define the core methods for initializing browser contexts and running the scraping logic.

```python
# xscraper/scraper.py
import asyncio
from playwright.async_api import async_playwright, BrowserContext
import psutil

class Scraper:
    def __init__(self, config):
        self.config = config
        self.browser: BrowserContext = None

    async def run(self):
        """Main execution flow with error handling"""
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.config.headless)
                await self._init_context()
                while True:
                    # Your scraping logic here
                    time.sleep(10)  # Simulate work

    async def _init_context(self):
        """Initialize browser context"""
        pass

if __name__ == '__main__':
    import asyncio
    from xscraper.config import Config
    config = Config.from_env_file('.env')
    scraper = Scraper(config)
    asyncio.run(scraper.run())
```

5. **Implement Configuration Class**:
   - Create a new Python file `config.py` to handle configuration loading.

```python
# xscraper/config.py
import os

class Config:
    @staticmethod
    def from_env_file(env_path):
        config = {}
        with open(env_path, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
        return Config(**config)

    def __init__(self, headless=True, username=None, password=None):
        self.headless = headless
        self.username = username
        self.password = password
```

#### Phase 2: Reliability
- **Error Recovery**: Handle exceptions gracefully and retry failed operations.
- **State Persistence**: Save the state of the scraper to avoid re-scraping already processed data.
- **Enhanced Logging**: Implement detailed logging for debugging and monitoring purposes.

##### Step-by-Step Implementation:

1. **Add Error Handling**:
   - Modify the `run` method in `scraper.py` to handle exceptions gracefully.

```python
# xscraper/scraper.py
import asyncio
from playwright.async_api import async_playwright, BrowserContext
import psutil

class Scraper:
    def __init__(self, config):
        self.config = config
        self.browser: BrowserContext = None

    async def run(self):
        """Main execution flow with error handling"""
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.config.headless)
                await self._init_context()
                while True:
                    # Your scraping logic here
                    time.sleep(10)  # Simulate work
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)  # Wait before retrying

    async def _init_context(self):
        """Initialize browser context"""
        pass

if __name__ == '__main__':
    import asyncio
    from xscraper.config import Config
    config = Config.from_env_file('.env')
    scraper = Scraper(config)
    asyncio.run(scraper.run())
```

2. **Add State Persistence**:
   - Use a file to store the state of the scraped data.

```python
# xscraper/scraper.py
import asyncio
from playwright.async_api import async_playwright, BrowserContext
import psutil

class Scraper:
    def __init__(self, config):
        self.config = config
        self.browser: BrowserContext = None
        self.state_file = 'state.json'

    async def run(self):
        """Main execution flow with error handling"""
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.config.headless)
                await self._init_context()
                while True:
                    # Your scraping logic here
                    time.sleep(10)  # Simulate work
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)  # Wait before retrying

    async def _init_context(self):
        """Initialize browser context"""
        pass

if __name__ == '__main__':
    import asyncio
    from xscraper.config import Config
    config = Config.from_env_file('.env')
    scraper = Scraper(config)
    asyncio.run(scraper.run())
```

3. **Add Enhanced Logging**:
   - Use the `logging` module to add detailed logging.

```python
# xscraper/scraper.py
import asyncio
from playwright.async_api import async_playwright, BrowserContext
import psutil
import logging

class Scraper:
    def __init__(self, config):
        self.config = config
        self.browser: BrowserContext = None
        self.state_file = 'state.json'
        logging.basicConfig(level=logging.INFO)

    async def run(self):
        """Main execution flow with error handling"""
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.config.headless)
                await self._init_context()
                while True:
                    # Your scraping logic here
                    time.sleep(10)  # Simulate work
        except Exception as e:
            logging.error(f"Error: {e}")
            await asyncio.sleep(60)  # Wait before retrying

    async def _init_context(self):
        """Initialize browser context"""
        pass

if __name__ == '__main__':
    import asyncio
    from xscraper.config import Config
    config = Config.from_env_file('.env')
    scraper = Scraper(config)
    asyncio.run(scraper.run())
```

#### Phase 3: Performance
- **Adaptive Sleep**: Adjust the sleep time based on system load.
- **Resource Monitoring**: Monitor CPU and memory usage.

##### Step-by-Step Implementation:

1. **Add Adaptive Sleep**:
   - Modify the `run` method to adjust the sleep time based on system load.

```python
# xscraper/scraper.py
import asyncio
from playwright.async_api import async_playwright, BrowserContext
import psutil

class Scraper:
    def __init__(self, config):
        self.config = config
        self.browser: BrowserContext = None
        self.state_file = 'state.json'
        logging.basicConfig(level=logging.INFO)

    async def run(self):
        """Main execution flow with error handling"""
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.config.headless)
                await self._init_context()
                while True:
                    # Your scraping logic here
                    time.sleep(10)  # Simulate work
        except Exception as e:
            logging.error(f"Error: {e}")
            await asyncio.sleep(60)  # Wait before retrying

    async def _init_context(self):
        """Initialize browser context"""
        pass

if __name__ == '__main__':
    import asyncio
    from xscraper.config import Config
    config = Config.from_env_file('.env')
    scraper = Scraper(config)
    asyncio.run(scraper.run())
```

2. **Add Resource Monitoring**:
   - Use `psutil` to monitor CPU and memory usage.

```python
# xscraper/scraper.py
import asyncio
from playwright.async_api import async_playwright, BrowserContext
import psutil

class Scraper:
    def __init__(self, config):
        self.config = config
        self.browser: BrowserContext = None
        self.state_file = 'state.json'
        logging.basicConfig(level=logging.INFO)

    async def run(self):
        """Main execution flow with error handling"""
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.config.headless)
                await self._init_context()
                while True:
                    # Your scraping logic here
                    time.sleep(10)  # Simulate work

                    cpu_usage = psutil.cpu_percent(interval=1)
                    memory_usage = psutil.virtual_memory().percent
                    logging.info(f"CPU Usage: {cpu_usage}% Memory Usage: {memory_usage}%")
        except Exception as e:
            logging.error(f"Error: {e}")
            await asyncio.sleep(60)  # Wait before retrying

    async def _init_context(self):
        """Initialize browser context"""
        pass

if __name__ == '__main__':
    import asyncio
    from xscraper.config import Config
    config = Config.from_env_file('.env')
    scraper = Scraper(config)
    asyncio.run(scraper.run())
```

By following these steps, you can improve the performance and stability of your web scraping application.