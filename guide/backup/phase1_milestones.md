# Phase 1: Core Functionality

## Milestone 1: Authentication System
**Objective**: Secure login with cookie persistence

**Components**:
- Cookie management
- Manual login flow
- Session validation

**Code**:
```python
# auth/session.py
class SessionManager:
    def __init__(self, config):
        self.cookie_path = config.cookie_path
        
    async def login(self, browser):
        if cookies := load_cookies(self.cookie_path):
            return await use_cookies(browser, cookies)
        return await manual_login(browser)
```

## Milestone 2: Search Implementation
**Objective**: Basic post search & filtering

**Components**:
- Keyword search
- Infinite scroll
- Post filtering

**Code**:
```python
# scraping/search.py
async def search_posts(keyword, min_likes):
    posts = []
    while len(posts) < 100:  # Safety limit
        await page.scroll_down()
        new_posts = await extract_posts()
        posts += [p for p in new_posts if p.likes >= min_likes]
    return posts
```

## Milestone 3: Profile Validation
**Objective**: Follower count extraction

**Components**:
- Profile page navigation
- Follower text parsing
- Basic validation

**Code**:
```python
# scraping/profile.py
def parse_followers(text):
    multipliers = {'K': 1000, 'M': 1_000_000}
    clean = text.upper().replace(',', '')
    if suffix := clean[-1]:
        return int(float(clean[:-1]) * multipliers[suffix])
    return int(clean)
```

## Milestone 4: Data Output
**Objective**: JSON results with basic info

**Components**:
- Result validation
- File export
- Progress display

**Code**:
```python
# output/manager.py
class ResultManager:
    def __init__(self, output_dir):
        self.results = []
        self.output_dir = output_dir
        
    def add(self, profile):
        if profile.is_valid:
            self.results.append(profile)
            
    def save(self):
        with open(self.output_dir / "results.json", 'w') as f:
            json.dump([p.to_dict() for p in self.results], f)
```

## Phase Completion Criteria
- [ ] User can login manually
- [ ] Search returns relevant posts
- [ ] Profiles validated for followers
- [ ] Results saved as JSON