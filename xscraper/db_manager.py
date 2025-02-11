from datetime import datetime
from typing import List, Tuple, Dict, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from .models import Tweet

class DBManager:
    """Manages database operations"""
    
    def __init__(self, uri: str):
        self.uri = uri
        self.client = None
        self.db = None
        
    def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client.get_database()
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
            
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    # Database Management
    def get_all_databases(self) -> List[Dict]:
        """Get all game databases with their stats"""
        try:
            databases = self.db.game_databases.find()
            result = []
            for db in databases:
                profile_count = self.db.profiles.count_documents({'database_id': db['_id']})
                active_profiles = self.db.profiles.count_documents({
                    'database_id': db['_id'],
                    'active': True
                })
                record_count = self.db.scraped_data.count_documents({'database_id': db['_id']})
                
                result.append({
                    '_id': db['_id'],
                    'name': db['name'],
                    'slug': db['slug'],
                    'profile_count': profile_count,
                    'active_profiles': active_profiles,
                    'record_count': record_count,
                    'last_updated': db.get('last_updated')
                })
            return result
        except Exception as e:
            print(f"Failed to get databases: {e}")
            return []

    def get_database(self, slug: str) -> Optional[Dict]:
        """Get a specific game database by slug"""
        return self.db.game_databases.find_one({'slug': slug})

    def add_database(self, name: str, slug: str) -> bool:
        """Add a new game database"""
        try:
            self.db.game_databases.insert_one({
                'name': name,
                'slug': slug,
                'created_at': datetime.utcnow(),
                'last_updated': None
            })
            return True
        except Exception as e:
            print(f"Failed to add database: {e}")
            return False

    def delete_database(self, slug: str) -> bool:
        """Delete a game database and all its data"""
        try:
            db = self.db.game_databases.find_one({'slug': slug})
            if db:
                # Delete all profiles and scraped data for this database
                self.db.profiles.delete_many({'database_id': db['_id']})
                self.db.scraped_data.delete_many({'database_id': db['_id']})
                self.db.game_databases.delete_one({'_id': db['_id']})
            return True
        except Exception as e:
            print(f"Failed to delete database: {e}")
            return False

    # Profile Management
    def get_profiles(self, database_id: ObjectId) -> List[Dict]:
        """Get all profiles for a specific database"""
        try:
            profiles = list(self.db.profiles.find({'database_id': database_id}))
            for profile in profiles:
                profile['record_count'] = self.db.scraped_data.count_documents({
                    'database_id': database_id,
                    'profile_id': profile['_id']
                })
            return profiles
        except Exception as e:
            print(f"Failed to get profiles: {e}")
            return []

    def get_active_profiles(self, database_id: ObjectId) -> List[Dict]:
        """Get active profiles for a specific database"""
        try:
            return list(self.db.profiles.find({
                'database_id': database_id,
                'active': True
            }))
        except Exception as e:
            print(f"Failed to get active profiles: {e}")
            return []

    def add_profile(self, database_id: ObjectId, url: str, description: str = None) -> bool:
        """Add a new profile to a database"""
        try:
            self.db.profiles.insert_one({
                'database_id': database_id,
                'url': url,
                'description': description,
                'active': True,
                'added_at': datetime.utcnow(),
                'last_scraped': None
            })
            return True
        except Exception as e:
            print(f"Failed to add profile: {e}")
            return False

    def toggle_profile(self, profile_id: ObjectId) -> bool:
        """Toggle profile active status"""
        try:
            profile = self.db.profiles.find_one({'_id': profile_id})
            if profile:
                self.db.profiles.update_one(
                    {'_id': profile_id},
                    {'$set': {'active': not profile.get('active', True)}}
                )
            return True
        except Exception as e:
            print(f"Failed to toggle profile: {e}")
            return False

    def delete_profile(self, profile_id: ObjectId) -> bool:
        """Delete a profile and its scraped data"""
        try:
            self.db.scraped_data.delete_many({'profile_id': profile_id})
            self.db.profiles.delete_one({'_id': profile_id})
            return True
        except Exception as e:
            print(f"Failed to delete profile: {e}")
            return False

    # Data Management
    async def save_tweets(self, database_id: ObjectId, profile_id: ObjectId, tweets: List[Tweet]) -> Tuple[int, int]:
        """Save tweets to database, returns (saved_count, duplicate_count)"""
        saved = 0
        duplicates = 0
        
        for tweet in tweets:
            try:
                result = self.db.scraped_data.update_one(
                    {
                        'database_id': database_id,
                        'profile_id': profile_id,
                        'id': tweet.id
                    },
                    {
                        '$setOnInsert': {
                            'database_id': database_id,
                            'profile_id': profile_id,
                            'id': tweet.id,
                            'text': tweet.text,
                            'created_at': tweet.created_at,
                            'author_username': tweet.author_username,
                            'scraped_at': datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
                if result.upserted_id:
                    saved += 1
                else:
                    duplicates += 1
                    
            except Exception as e:
                print(f"Failed to save tweet {tweet.id}: {e}")
                
        if saved > 0:
            self.update_database_last_updated(database_id)
                
        return saved, duplicates

    def update_profile_last_scraped(self, profile_id: ObjectId):
        """Update the last_scraped timestamp for a profile"""
        try:
            self.db.profiles.update_one(
                {'_id': profile_id},
                {'$set': {'last_scraped': datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Failed to update last_scraped for profile {profile_id}: {e}")

    def update_database_last_updated(self, database_id: ObjectId):
        """Update the last_updated timestamp for a database"""
        try:
            self.db.game_databases.update_one(
                {'_id': database_id},
                {'$set': {'last_updated': datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Failed to update last_updated for database {database_id}: {e}")