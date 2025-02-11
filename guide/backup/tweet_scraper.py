import asyncio
from pyppeteer import errors

class TweetScraper:
    def __init__(self, db_handler, browser, profile_queue, min_likes, max_likes, min_followers, max_followers, max_influencers): # Added max_likes, max_followers, max_influencers
        self.db = db_handler
        self.browser = browser
        self.profile_queue = profile_queue
        self.min_likes = min_likes
        self.max_likes = max_likes # Added
        self.min_followers = min_followers
        self.max_followers = max_followers # Added
        self.max_influencers = max_influencers # Added

    async def scrape(self, search_term, min_likes):
        """Scrape tweets and queue valid profiles"""
        page = await self.browser.newPage()
        try:
            await page.setViewport({'width': 1280, 'height': 800})
            await page.goto(f"https://x.com/search?q={search_term}&src=typed_query")
            print(f"🚀 Started scraping: {search_term}")

            while True:
                try:
                    await page.waitForSelector('article[data-testid="tweet"]', {'timeout': 10000})
                    tweets = await page.querySelectorAll('article[data-testid="tweet"]')
                    print(f"🔍 Found {len(tweets)} tweets")

                    for tweet in tweets:
                        try:
                            # Extract profile URL
                            profile_element = await tweet.querySelector('div[data-testid="User-Name"] a[href^="/"]')
                            if not profile_element:
                                continue

                            profile_url = f"https://x.com{await profile_element.evaluate('el => el.getAttribute("href")')}"

                            # Extract content
                            content_element = await tweet.querySelector('div[data-testid="tweetText"]')
                            content = await content_element.evaluate('el => el.textContent') if content_element else ""

                            # Get metrics
                            likes = await self._get_metric(tweet, 'like')
                            followers = await self._get_followers(profile_url)

                            if followers >= self.min_followers and likes >= self.min_likes: # Use self.min_likes here
                                self.db.add_tweet({
                                    "content": content,
                                    "likes": likes,
                                    "retweets": await self._get_metric(tweet, 'retweet'),
                                    "replies": await self._get_metric(tweet, 'reply'),
                                    "views": await self._get_metric(tweet, 'view'),
                                    "profile_url": profile_url,
                                    "followers": followers
                                })
                                await self.profile_queue.put(profile_url)
                                print(f"✅ Qualified: {content[:50]}... ({likes} likes, {followers} followers)")

                        except Exception as e:
                            print(f"⚠️ Tweet error: {str(e)}")

                    # Scroll to load more
                    await page.evaluate('window.scrollBy(0, window.innerHeight)')
                    await asyncio.sleep(2)

                except Exception as e: # Corrected indentation and try block
                    print(f"⚠️ Page error: {str(e)}")
                    break # Corrected indentation

            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await asyncio.sleep(2)

            # Removed extra indented lines here

        except Exception as e:
            print(f"Scraping failed: {str(e)}")
        finally:
            await page.close()
            page = await self.browser.newPage()
            await page.setViewport({'width': 1280, 'height': 800})

            url = f"https://x.com/search?q={search_term}&src=typed_query"
            await page.goto(url)
            print(f"Started scraping tweets for: {search_term}")

            # Implement actual scraping logic here
            while True:
                # Wait for tweets to load
                await page.waitForSelector('article[data-testid="tweet"]', {'timeout': 10000})

                # Extract and process tweets
                tweets = await page.querySelectorAll('article[data-testid="tweet"]')
                print(f"Found {len(tweets)} tweets on page")

                for tweet in tweets:
                    try:
                        # Extract profile details first
                        profile_element = await tweet.querySelector('div[data-testid="User-Name"] a[href^="/"][role="link"]')
                        if not profile_element:
                            print("Debug: No profile element found in tweet")
                            continue

                        profile_url = f"https://x.com{await profile_element.evaluate('el => el.getAttribute("href")')}"
                        print(f"Debug: Found profile URL: {profile_url}")

                        # Extract tweet content
                        content_element = await tweet.querySelector('div[data-testid="tweetText"]')
                        content = await content_element.evaluate('el => el.textContent') if content_element else ""

                        # Extract engagement metrics with fallbacks
                        likes = await self._get_metric(tweet, 'like')
                        retweets = await self._get_metric(tweet, 'retweet')
                        replies = await self._get_metric(tweet, 'reply')
                        views = await self._get_metric(tweet, 'view')

                        # Get follower count directly from profile page
                        followers = await self._get_followers(profile_url)

                        # Store data if meets criteria
                        if followers >= self.min_followers and likes >= self.min_likes: # Use self.min_likes here
                            tweet_data = {
                                "content": content,
                                "likes": likes,
                                "retweets": retweets,
                                "replies": replies,
                                "views": views,
                                "profile_url": profile_url,
                                "followers": followers
                            }

                            self.db.add_tweet(tweet_data)
                            await self.profile_queue.put(profile_url)
                            print(f"✅ Qualified tweet: {content[:50]}... ({likes} likes, {followers} followers)")

                    except Exception as e:
                        print(f"⚠️ Error processing tweet: {str(e)}")
                        continue

                # Scroll to load more tweets
                await page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(2)

                # Scroll to load more tweets
                await page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(2)

        except Exception as e: # Corrected indentation and try block
            print(f"Scraping failed: {str(e)}")
        finally: # Corrected indentation and try block
            if not page.isClosed(): # Corrected indentation and try block
                await page.close()
            






































































    async def _get_metric(self, tweet, metric_type):
        element = await tweet.querySelector(f'div[data-testid="{metric_type}"]')
        if element:
            text = await element.evaluate('el => el.innerText')
            return int(text.replace(',', '')) if text else 0
        return 0

    async def _get_followers(self, profile_url):
        try:
            profile_page = await self.browser.newPage()
            await profile_page.goto(profile_url)
            await profile_page.waitForSelector('a[href$="/followers"]', {'timeout': 5000})
            follower_element = await profile_page.querySelector('a[href$="/followers"] span')
            followers_text = await follower_element.evaluate('el => el.textContent')
            return int(followers_text.replace(',', ''))
        except Exception as e:
            print(f"⚠️ Couldn't get followers for {profile_url}: {str(e)}")
            return 0
        finally:
            if 'profile_page' in locals():
                await profile_page.close()