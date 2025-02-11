#!/usr/bin/env python3
"""
Setup script for X Scraper
Installs dependencies and configures the environment
"""

import os
import sys
import subprocess
from pathlib import Path

def print_step(step: str):
    print(f"\n=== {step} ===")

def run_command(command: str) -> bool:
    """Run a shell command and return True if successful"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def create_virtual_env():
    """Create and activate virtual environment"""
    print_step("Creating virtual environment")
    
    if not run_command("python -m venv venv"):
        print("Failed to create virtual environment")
        return False
        
    # Print activation instructions
    if os.name == 'nt':  # Windows
        print("\nTo activate virtual environment, run:")
        print("venv\\Scripts\\activate")
    else:  # Unix
        print("\nTo activate virtual environment, run:")
        print("source venv/bin/activate")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step("Installing Python dependencies")
    
    dependencies = [
        "playwright",
        "python-dotenv",
        "pymongo",
        "pytest",
        "pytest-asyncio",
        "pytest-mongodb",
        "tqdm"
    ]
    
    # Create requirements.txt
    with open("requirements.txt", "w") as f:
        f.write("\n".join(dependencies))
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install Python dependencies")
        return False
    
    # Install Playwright browsers
    if not run_command("playwright install"):
        print("Failed to install Playwright browsers")
        return False
    
    return True

def setup_env():
    """Create .env file if it doesn't exist"""
    print_step("Setting up environment")
    
    if not os.path.exists(".env"):
        print("Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/xscraper

# Scraping Configuration
POSTS_LIMIT=30
HEADLESS=true
TARGET_PROFILES=profile1,profile2,profile3

# Browser Settings
TIMEOUT=45000

# Logging
LOG_LEVEL=INFO""")
        print("Created .env file - please edit with your settings")
    else:
        print(".env file already exists")

def setup_cron():
    """Help setup cron job"""
    print_step("Cron job setup")
    
    if os.name == 'nt':  # Windows
        print("For Windows, use Task Scheduler:")
        print("1. Open Task Scheduler")
        print("2. Create Basic Task")
        print("3. Set trigger to run every 6 hours")
        print(f"4. Action: Start a program")
        print(f"5. Program/script: {sys.executable}")
        print(f"6. Arguments: {os.path.abspath('scraper_job.py')}")
        print(f"7. Start in: {os.path.abspath('.')}")
    else:
        print("To setup cron job, run: crontab -e")
        print("Add the following line:")
        print(f"0 */6 * * * cd {os.path.abspath('.')} && {sys.executable} scraper_job.py")

def main():
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("X Scraper Setup\n")
    
    # Create virtual environment
    if not create_virtual_env():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_env()
    
    # Help with cron setup
    setup_cron()
    
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("1. Activate virtual environment")
    print("2. Edit .env with your settings")
    print("3. Run python scripts/test_mongodb.py to verify MongoDB connection")
    print("4. Setup cron job as described above")

if __name__ == "__main__":
    main()