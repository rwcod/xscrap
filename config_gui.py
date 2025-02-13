import os
import sys
import json

class ConfigManager:
    def __init__(self):
        """Initialize configuration manager in CLI-only mode"""
        self.create_config_cli()

    def create_config_cli(self):
        """Create configuration through command line interface"""
        config = {}
        
        print("XScraper Configuration")
        print("=====================")
        
        # Get configuration values through CLI
        config['base_url'] = input("Enter base URL: ").strip() or "https://x.com"
        config['username'] = input("Enter username: ").strip()
        config['viewport_width'] = input("Enter viewport width (default 1280): ").strip() or "1280"
        config['viewport_height'] = input("Enter viewport height (default 720): ").strip() or "720"
        config['headless'] = input("Run in headless mode? (y/n, default: y): ").strip().lower() != 'n'
        
        # Save configuration
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"\nConfiguration saved to {config_path}")
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    ConfigManager()