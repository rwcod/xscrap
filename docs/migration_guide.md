# Migration Guide: X Scraper Refactoring

## Overview of Changes

Moving from the current implementation to MongoDB-based version with simplified data model and scheduled execution.

## Files to be Modified

### 1. models.py
Current:
```python
@dataclass
class Tweet:
    id: str
    text: str
    created_at: datetime
    likes: int
    retweets: int
    author_username: str
    
@dataclass
class Profile:
    username: str
    display_name: str
    followers: int
    following: int
    bio: Optional[str] = None
    tweets: List[Tweet] = None
```

New:
```python
@dataclass
class Tweet:
    id: str
    text: str
    created_at: datetime
    author_username: str
```

### 2. scraper.py
Current functionality to remove:
- Profile metrics collection
- Tweet metrics collection
- Search functionality

New functionality to add:
- Profile-specific post collection
- MongoDB integration
- Post limit configuration

### 3. config.py
To remove:
- GUI-related code
- Metrics thresholds

To add:
- MongoDB configuration
- Profile list configuration
- Posts limit configuration

## New Files to Create

1. `db_manager.py` - MongoDB integration
2. `scraper_job.py` - Main execution script for cron

## Files to Remove

1. `config_gui.py` - No longer needed
2. GUI-related imports from other files

## Database Migration

No data migration needed as we're starting fresh with MongoDB.

## Configuration Changes

### Old (.env):
```
HEADLESS=true
MAX_CONCURRENT=5
TARGET_KEYWORD=example
MIN_PROFILE_FOLLOWERS=1000
MIN_POST_LIKES=100
```

### New (.env):
```
MONGODB_URI=mongodb://localhost:27017/xscraper
POSTS_LIMIT=30
HEADLESS=true
TARGET_PROFILES=profile1,profile2,profile3
```

## Testing Updates

1. Remove tests for:
- Profile metrics
- Tweet metrics
- GUI functionality

2. Add tests for:
- MongoDB integration
- Profile post collection
- Deduplication logic

## Deployment Changes

1. Remove:
- GUI launch options
- Metrics-related parameters

2. Add:
- MongoDB setup
- Cron job configuration
- Database indexes creation

## Backup Plan

1. Keep copy of old code before making changes
2. Document all removed functionality
3. Maintain old configuration files for reference

## Rollback Procedure

1. How to restore previous version if needed
2. Steps to remove MongoDB changes
3. How to disable cron jobs

## Timeline

1. Phase 1: Setup MongoDB (1 day)
2. Phase 2: Code Modifications (2-3 days)
3. Phase 3: Testing (1-2 days)
4. Phase 4: Deployment & Monitoring (1 day)

## Support Considerations

1. Things that might break:
- Existing scripts using old config format
- Custom integrations with current output
- Any dependent processes

2. Required updates for:
- Documentation
- Monitoring scripts
- Deployment procedures

## Success Criteria

1. All target profiles successfully scraped
2. Posts correctly stored in MongoDB
3. Deduplication working properly
4. Cron jobs running on schedule
5. Error handling functioning as expected
6. Logs providing adequate information

## Monitoring Changes

1. New metrics to track:
- MongoDB connection status
- Post collection success rate
- Deduplication rate
- Cron job execution status

2. Remove monitoring for:
- GUI events
- Metrics collection
- Search operations

## Documentation Updates Needed

1. README.md updates
2. API documentation changes
3. Configuration guide updates
4. New MongoDB setup guide
5. Cron setup instructions