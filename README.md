# X Scraper

A Python-based tool for scraping posts from X (Twitter) profiles and storing them in MongoDB. The scraper runs automatically every 6 hours to collect the latest posts.

## Docker Setup (Recommended)

### Prerequisites
- Docker Desktop installed
- At least 2GB free space on drive E:

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd xscraper
```

2. Configure your profiles:
Edit `docker-compose.yml` and update the `TARGET_PROFILES` environment variable with your desired X profiles:
```yaml
environment:
  - TARGET_PROFILES=profile1,profile2,profile3
```

3. Start the services:
```bash
docker-compose up -d
```

This will:
- Create necessary directories on drive E:
- Start MongoDB container with data stored at `E:/xscraper/mongodb`
- Start the scraper container
- Configure automatic running every 6 hours

### Directory Structure on E: Drive

```
E:/xscraper/
├── mongodb/        # MongoDB data files
├── logs/           # Application logs
└── auth/           # Authentication data
```

### Monitoring

View logs:
```bash
docker-compose logs -f scraper
```

Check MongoDB data:
```bash
docker exec -it xscraper-mongodb mongosh
use xscraper
db.tweets.find().sort({created_at: -1}).limit(5)
```

### Stopping the Service

```bash
docker-compose down
```

## Manual Setup (Alternative)

If you prefer not to use Docker, follow these steps for manual installation:

1. Install MongoDB:
```bash
# Ubuntu
sudo apt-get install mongodb

# macOS
brew install mongodb-community
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
playwright install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Setup cron job:
```bash
crontab -e
# Add: 0 */6 * * * cd /path/to/xscraper && python main.py
```

## Configuration

Key settings in docker-compose.yml (for Docker setup):
```yaml
environment:
  - MONGODB_URI=mongodb://mongodb:27017/xscraper
  - POSTS_LIMIT=30
  - TARGET_PROFILES=profile1,profile2,profile3
  - LOG_LEVEL=INFO
  - HEADLESS=true
```

Or in .env file (for manual setup):
```
MONGODB_URI=mongodb://localhost:27017/xscraper
POSTS_LIMIT=30
TARGET_PROFILES=profile1,profile2,profile3
HEADLESS=true
```

## Project Structure

```
xscraper/
├── docker-compose.yml   # Docker configuration
├── Dockerfile          # Docker build instructions
├── config/            # Scheduler configuration
├── docs/              # Documentation
├── xscraper/          # Main package
│   ├── __init__.py
│   ├── auth.py       # X authentication
│   ├── config.py     # Configuration management
│   ├── db_manager.py # MongoDB integration
│   ├── models.py     # Data models
│   └── scraper.py    # Core scraping logic
├── scripts/          # Utility scripts
└── requirements.txt  # Python dependencies
```

## Development

1. Build the Docker image:
```bash
docker-compose build
```

2. Run tests:
```bash
docker-compose run --rm scraper pytest
```

3. Check logs:
```bash
docker-compose logs -f
```

## Troubleshooting

1. If MongoDB fails to start:
- Ensure drive E: has sufficient space
- Check permissions on E:/xscraper directory
- Review logs: `docker-compose logs mongodb`

2. If scraper fails:
- Check authentication: Verify auth.json in E:/xscraper/auth
- Review logs: `docker-compose logs scraper`
- Ensure MongoDB is running: `docker-compose ps`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.