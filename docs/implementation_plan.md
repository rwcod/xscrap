# X Scraper Implementation Plan

## 1. Database Setup
- [ ] Install and configure MongoDB
  - [ ] Add MongoDB connection string to .env
  - [ ] Create database connection utility
  - [ ] Setup indexes for tweet deduplication

## 2. Code Structure Changes
### Models (models.py)
- [ ] Simplify Tweet model
  - [ ] Remove metrics fields (likes, retweets)
  - [ ] Keep only: id, text, author_username, created_at
- [ ] Remove Profile model (no longer needed)
- [ ] Add MongoDB model/schema definitions

### Config (config.py)
- [ ] Remove GUI-related code (no longer needed)
- [ ] Add MongoDB configuration
- [ ] Add new settings:
  - [ ] MONGODB_URI
  - [ ] POSTS_LIMIT (20-30)
  - [ ] TARGET_PROFILES (list of X profiles to track)

### Scraper (scraper.py)
- [ ] Update scraper to focus on profile posts
  - [ ] Remove metrics collection code
  - [ ] Add method for getting N most recent posts
  - [ ] Implement MongoDB integration
  - [ ] Add deduplication logic
- [ ] Implement error handling for rate limits

## 3. Database Integration
- [ ] Create db_manager.py
  - [ ] MongoDB connection handling
  - [ ] CRUD operations for tweets
  - [ ] Deduplication logic
  - [ ] Query methods for data retrieval

## 4. Cron Job Setup
- [ ] Create scraper_job.py script
  - [ ] Main execution logic
  - [ ] Error handling
  - [ ] Logging
- [ ] Create crontab configuration
  - [ ] Setup 6-hour interval
  - [ ] Logging for cron execution

## 5. Testing
- [ ] Update test_scraper.py
  - [ ] Add MongoDB mocking
  - [ ] Test deduplication
  - [ ] Test profile scraping
- [ ] Add new tests for db_manager.py
- [ ] Add integration tests

## 6. Documentation
- [ ] Update README.md with:
  - [ ] MongoDB setup instructions
  - [ ] Cron setup instructions
  - [ ] New configuration options
  - [ ] Usage examples

## 7. Dependencies
- [ ] Update requirements.txt
  ```
  pymongo
  python-dotenv
  playwright
  pytest
  pytest-asyncio
  pytest-mongodb
  ```

## Implementation Order
1. Database setup & integration
2. Core scraper modifications
3. Cron job implementation
4. Testing & validation
5. Documentation update

## Notes
- Ensure proper error handling for network issues
- Implement logging for monitoring scraping process
- Consider implementing backup mechanism for MongoDB
- Plan for scalability (multiple profiles, rate limiting)