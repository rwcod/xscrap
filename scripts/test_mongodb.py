#!/usr/bin/env python3
"""
MongoDB connection test script.
This script helps verify your MongoDB connection and creates required indexes.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionError, OperationFailure

def test_connection(uri: str) -> bool:
    """Test MongoDB connection and setup"""
    print(f"Testing MongoDB connection...")
    
    try:
        # Try to connect
        client = MongoClient(uri)
        db = client.xscraper
        
        # Test connection with ping
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB")
        
        # Create indexes
        print("Setting up indexes...")
        db.tweets.create_index([("tweet_id", 1)], unique=True)
        print("✓ Created unique index on tweet_id")
        
        # Test insert
        print("Testing write operations...")
        result = db.tweets.insert_one({
            "tweet_id": "test_" + datetime.now().isoformat(),
            "text": "Test tweet",
            "author_username": "test_user",
            "created_at": datetime.now(),
            "scraped_at": datetime.now()
        })
        print("✓ Successfully inserted test document")
        
        # Clean up test document
        db.tweets.delete_one({"_id": result.inserted_id})
        print("✓ Successfully cleaned up test document")
        
        # Close connection
        client.close()
        print("\nAll tests passed! MongoDB is configured correctly.")
        return True
        
    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nPossible solutions:")
        print("1. Check if MongoDB is running")
        print("2. Verify your connection string")
        print("3. Check if MongoDB is accepting connections (firewall settings)")
        return False
        
    except OperationFailure as e:
        print(f"\n❌ Operation Error: {e}")
        print("\nPossible solutions:")
        print("1. Check if you have proper permissions")
        print("2. Verify authentication credentials")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI
    uri = os.getenv('MONGODB_URI')
    if not uri:
        print("❌ Error: MONGODB_URI not found in environment variables")
        print("\nPlease set MONGODB_URI in your .env file:")
        print('MONGODB_URI=mongodb://localhost:27017/xscraper')
        sys.exit(1)
    
    # Test connection
    success = test_connection(uri)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()