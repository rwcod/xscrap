import os
import json
import csv
from datetime import datetime
from pymongo import MongoClient
import pandas as pd

def connect_to_db():
    """Connect to MongoDB"""
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/xscraper")
    client = MongoClient(mongodb_uri)
    return client.get_default_database()

def export_to_json(db, output_dir="exports"):
    """Export all scraped data to JSON files per profile"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all databases
        databases = list(db.game_databases.find())
        
        for database in databases:
            db_dir = os.path.join(output_dir, database['slug'])
            os.makedirs(db_dir, exist_ok=True)
            
            # Get all profiles for this database
            profiles = list(db.profiles.find({'database_id': database['_id']}))
            
            for profile in profiles:
                # Get records for this profile
                records = list(db.scraped_data.find({
                    'database_id': database['_id'],
                    'profile_id': profile['_id']
                }))
                
                # Convert ObjectId to string for JSON serialization
                for record in records:
                    record['_id'] = str(record['_id'])
                    record['database_id'] = str(record['database_id'])
                    record['profile_id'] = str(record['profile_id'])
                    # Convert datetime to ISO format
                    if 'timestamp' in record and isinstance(record['timestamp'], datetime):
                        record['timestamp'] = record['timestamp'].isoformat()
                    if 'scraped_at' in record and isinstance(record['scraped_at'], datetime):
                        record['scraped_at'] = record['scraped_at'].isoformat()
                
                # Save to JSON file
                filename = f"{profile['url'].split('/')[-1]}_{datetime.now().strftime('%Y%m%d')}.json"
                filepath = os.path.join(db_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                
                print(f"Exported {len(records)} records to {filepath}")
    except Exception as e:
        print(f"Error exporting to JSON: {str(e)}")
                
def export_to_csv(db, output_dir="exports"):
    """Export all scraped data to CSV files per profile"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all databases
        databases = list(db.game_databases.find())
        
        for database in databases:
            db_dir = os.path.join(output_dir, database['slug'])
            os.makedirs(db_dir, exist_ok=True)
            
            # Get all profiles for this database
            profiles = list(db.profiles.find({'database_id': database['_id']}))
            
            for profile in profiles:
                # Get records for this profile
                records = list(db.scraped_data.find({
                    'database_id': database['_id'],
                    'profile_id': profile['_id']
                }))
                
                if not records:
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(records)
                
                # Format datetime columns
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                if 'scraped_at' in df.columns:
                    df['scraped_at'] = pd.to_datetime(df['scraped_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Save to CSV file
                filename = f"{profile['url'].split('/')[-1]}_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = os.path.join(db_dir, filename)
                
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                print(f"Exported {len(records)} records to {filepath}")
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")

def main():
    """Main export function"""
    try:
        db = connect_to_db()
        
        print("Starting data export...")
        print("\nExporting to JSON...")
        export_to_json(db)
        
        print("\nExporting to CSV...")
        export_to_csv(db)
        
        print("\nExport completed successfully!")
        
    except Exception as e:
        print(f"Error during export: {str(e)}")

if __name__ == "__main__":
    main()