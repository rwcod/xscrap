from dotenv import load_dotenv
import os

class Config:
    def __init__(self, dev_mode=False, log_level='INFO', target_keyword='BTC', **kwargs):
        self.dev_mode = dev_mode
        self.headless = not dev_mode  # Dev mode → visible
        self.log_level = 'DEBUG' if dev_mode else log_level
        self.timeout = kwargs.get('timeout', 30000)
        self.max_concurrent = kwargs.get('max_concurrent', 5)
        self.target_keyword = target_keyword

    @classmethod
    def from_env_file(cls, env_path='.env'):
        load_dotenv(env_path)
        return cls(
            dev_mode=os.getenv('DEV_MODE', 'False') == 'True',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            timeout=int(os.getenv('TIMEOUT', '30000')),
            max_concurrent=int(os.getenv('MAX_CONCURRENT', '5')),
            target_keyword=os.getenv('TARGET_KEYWORD', 'BTC')
        ) 