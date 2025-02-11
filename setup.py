from setuptools import setup, find_packages

setup(
    name="xscraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'playwright',
        'python-dotenv',
        'tqdm'
        'playwright>=1.11.1',
        'python-dotenv>=0.19.0',
        'tqdm>=4.63.3'
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for scraping social media profiles based on specific criteria.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/xscraper"
) 