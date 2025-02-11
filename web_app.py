from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson import ObjectId
import os
import logging
import asyncio
from datetime import datetime
from xscraper.scraper import XScraper
from xscraper.utils import normalize_x_url, is_valid_x_url

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/xscraper")
app.config["DEBUG"] = True
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")

logger.info(f"Starting app with MongoDB URI: {app.config['MONGO_URI']}")

# Initialize MongoDB connection
try:
    mongo = PyMongo(app)
    mongo.db.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

async def scrape_profile_data(url, database_id, profile_id):
    """Scrape profile data and store in database"""
    try:
        # Initialize scraper
        scraper = XScraper(headless=True)
        await scraper.init_browser()
        
        try:
            # Scrape posts
            posts = await scraper.scrape_profile(url, max_posts=30)
            logger.info(f"Scraped {len(posts)} posts from {url}")
            
            if posts:
                # Store each post
                for post in posts:
                    # Add metadata
                    post['database_id'] = database_id
                    post['profile_id'] = profile_id
                    post['profile_url'] = url
                    post['last_updated'] = datetime.utcnow()
                    
                    # Update or insert post
                    mongo.db.scraped_data.update_one(
                        {
                            'database_id': database_id,
                            'profile_id': profile_id,
                            'id': post['id']
                        },
                        {'$set': post},
                        upsert=True
                    )
                
                # Update profile's last scraped time
                mongo.db.profiles.update_one(
                    {'_id': profile_id},
                    {
                        '$set': {
                            'last_scraped': datetime.utcnow(),
                            'last_scrape_count': len(posts)
                        }
                    }
                )
                
                # Update database's last updated time
                mongo.db.game_databases.update_one(
                    {'_id': database_id},
                    {'$set': {'last_updated': datetime.utcnow()}}
                )
                
                return len(posts)
            
            return 0
            
        finally:
            await scraper.close()
            
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return 0

def init_db():
    """Initialize database collections and indexes"""
    try:
        logger.info("Starting database initialization...")
        
        # Create indexes
        mongo.db.game_databases.create_index('slug', unique=True)
        mongo.db.profiles.create_index([('database_id', 1), ('url', 1)], unique=True)
        mongo.db.scraped_data.create_index([('database_id', 1), ('profile_id', 1), ('id', 1)], unique=True)
        logger.info("Created indexes")
        
        # Create default database if none exists
        default_db = mongo.db.game_databases.find_one({'slug': 'cs2'})
        if not default_db:
            try:
                result = mongo.db.game_databases.insert_one({
                    'name': 'Counter Strike 2',
                    'slug': 'cs2',
                    'created_at': datetime.utcnow(),
                    'last_updated': None
                })
                logger.info(f"Created default CS2 database with ID: {result.inserted_id}")
            except Exception as e:
                logger.warning(f"Could not create default database: {e}")
        else:
            logger.info("Default database already exists")
            
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

# Initialize database using app context
with app.app_context():
    init_db()

@app.route('/')
def index():
    try:
        databases = list(mongo.db.game_databases.find())
        stats = []
        for db in databases:
            record_count = mongo.db.scraped_data.count_documents({'database_id': db['_id']})
            profile_count = mongo.db.profiles.count_documents({'database_id': db['_id']})
            stats.append({
                'name': db['name'],
                'slug': db['slug'],
                'record_count': record_count,
                'profile_count': profile_count,
                'last_updated': db.get('last_updated')
            })
        return render_template('index.html', databases=stats)
    except Exception as e:
        logger.error(f"Index error: {str(e)}", exc_info=True)
        flash('An error occurred while loading the dashboard', 'danger')
        return render_template('index.html', databases=[])

@app.route('/databases', methods=['GET', 'POST'])
def databases():
    try:
        if request.method == 'POST':
            action = request.args.get('action')
            
            if action == 'delete':
                # Handle database deletion
                slug = request.args.get('slug')
                if slug:
                    db = mongo.db.game_databases.find_one({'slug': slug})
                    if db:
                        mongo.db.profiles.delete_many({'database_id': db['_id']})
                        mongo.db.scraped_data.delete_many({'database_id': db['_id']})
                        mongo.db.game_databases.delete_one({'_id': db['_id']})
                        flash('Database deleted successfully', 'success')
                    else:
                        flash('Database not found', 'danger')
            else:
                # Handle database creation
                name = request.form.get('name')
                slug = request.form.get('slug')
                
                if not name or not slug:
                    flash('Name and slug are required', 'danger')
                else:
                    try:
                        mongo.db.game_databases.insert_one({
                            'name': name,
                            'slug': slug,
                            'created_at': datetime.utcnow(),
                            'last_updated': None
                        })
                        flash('Database added successfully', 'success')
                    except Exception as e:
                        logger.error(f"Error adding database: {e}")
                        flash('A database with this slug already exists', 'danger')
            
            return redirect(url_for('databases'))
        
        # GET request - show databases
        databases = list(mongo.db.game_databases.find())
        logger.debug(f"Found {len(databases)} databases")
        
        db_list = []
        for db in databases:
            record_count = mongo.db.scraped_data.count_documents({'database_id': db['_id']})
            profile_count = mongo.db.profiles.count_documents({'database_id': db['_id']})
            db_list.append({
                '_id': db['_id'],
                'name': db['name'],
                'slug': db['slug'],
                'record_count': record_count,
                'profile_count': profile_count,
                'last_updated': db.get('last_updated')
            })
            
        return render_template('databases.html', databases=db_list)
    except Exception as e:
        logger.error(f"Databases error: {str(e)}", exc_info=True)
        flash('An error occurred while loading databases', 'danger')
        return render_template('databases.html', databases=[])

@app.route('/databases/<slug>')
def view_database(slug):
    try:
        database = mongo.db.game_databases.find_one({'slug': slug})
        if not database:
            flash('Database not found', 'danger')
            return redirect(url_for('databases'))
        
        profiles = list(mongo.db.profiles.find({'database_id': database['_id']}))
        active_profiles = sum(1 for p in profiles if p.get('active', True))
        total_records = mongo.db.scraped_data.count_documents({'database_id': database['_id']})
        
        for profile in profiles:
            profile['record_count'] = mongo.db.scraped_data.count_documents({
                'database_id': database['_id'],
                'profile_id': profile['_id']
            })
        
        return render_template('profiles.html',
                             database=database,
                             profiles=profiles,
                             active_profiles=active_profiles,
                             total_records=total_records)
    except Exception as e:
        logger.error(f"View database error: {str(e)}", exc_info=True)
        flash('An error occurred while loading the database', 'danger')
        return redirect(url_for('databases'))

@app.route('/databases/<slug>/profiles/add', methods=['POST'])
def add_profile(slug):
    try:
        database = mongo.db.game_databases.find_one({'slug': slug})
        if not database:
            flash('Database not found', 'danger')
            return redirect(url_for('databases'))
        
        url = request.form.get('profile_url')
        description = request.form.get('description', '')
        
        if not url:
            flash('Profile URL is required', 'danger')
            return redirect(url_for('view_database', slug=slug))
        
        # Normalize and validate the URL
        normalized_url = normalize_x_url(url)
        if not is_valid_x_url(normalized_url):
            flash('Invalid X/Twitter profile URL', 'danger')
            return redirect(url_for('view_database', slug=slug))
        
        # Check if profile already exists
        existing_profile = mongo.db.profiles.find_one({
            'database_id': database['_id'],
            'url': normalized_url
        })
        
        if existing_profile:
            flash('Profile already exists in this database', 'warning')
        else:
            new_profile = {
                'database_id': database['_id'],
                'url': normalized_url,
                'description': description,
                'active': True,
                'added_at': datetime.utcnow(),
                'last_scraped': None,
                'record_count': 0
            }
            mongo.db.profiles.insert_one(new_profile)
            flash('Profile added successfully', 'success')
        
        return redirect(url_for('view_database', slug=slug))
    except Exception as e:
        logger.error(f"Add profile error: {str(e)}", exc_info=True)
        flash('An error occurred while adding the profile', 'danger')
        return redirect(url_for('view_database', slug=slug))

@app.route('/databases/<slug>/profiles/scrape', methods=['POST'])
def scrape_profiles(slug):
    """Scrape all active profiles in a database"""
    try:
        database = mongo.db.game_databases.find_one({'slug': slug})
        if not database:
            flash('Database not found', 'danger')
            return redirect(url_for('databases'))
        
        # Get all active profiles
        profiles = list(mongo.db.profiles.find({
            'database_id': database['_id'],
            'active': True
        }))
        
        if not profiles:
            flash('No active profiles found', 'warning')
            return redirect(url_for('view_database', slug=slug))
        
        total_scraped = 0
        for profile in profiles:
            # Run scraping in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                posts_count = loop.run_until_complete(
                    scrape_profile_data(profile['url'], database['_id'], profile['_id'])
                )
                total_scraped += posts_count
            finally:
                loop.close()
        
        flash(f'Successfully scraped {total_scraped} posts from {len(profiles)} profiles', 'success')
        
    except Exception as e:
        logger.error(f"Scrape profiles error: {str(e)}", exc_info=True)
        flash('An error occurred while scraping profiles', 'danger')
    
    return redirect(url_for('view_database', slug=slug))

@app.route('/databases/<slug>/profiles/<profile_id>/toggle', methods=['POST'])
def toggle_profile(slug, profile_id):
    try:
        profile = mongo.db.profiles.find_one({'_id': ObjectId(profile_id)})
        if not profile:
            flash('Profile not found', 'danger')
            return redirect(url_for('view_database', slug=slug))
        
        new_status = not profile.get('active', True)
        mongo.db.profiles.update_one(
            {'_id': ObjectId(profile_id)},
            {'$set': {'active': new_status}}
        )
        
        status_text = 'activated' if new_status else 'deactivated'
        flash(f'Profile {status_text} successfully', 'success')
        return redirect(url_for('view_database', slug=slug))
    except Exception as e:
        logger.error(f"Toggle profile error: {str(e)}", exc_info=True)
        flash('An error occurred while toggling the profile', 'danger')
        return redirect(url_for('view_database', slug=slug))

@app.route('/databases/<slug>/profiles/<profile_id>/delete', methods=['POST'])
def delete_profile(slug, profile_id):
    try:
        profile = mongo.db.profiles.find_one({'_id': ObjectId(profile_id)})
        if profile:
            # Delete profile's records first
            mongo.db.scraped_data.delete_many({'profile_id': ObjectId(profile_id)})
            # Then delete the profile
            mongo.db.profiles.delete_one({'_id': ObjectId(profile_id)})
            flash('Profile and its data deleted successfully', 'success')
        else:
            flash('Profile not found', 'danger')
        return redirect(url_for('view_database', slug=slug))
    except Exception as e:
        logger.error(f"Delete profile error: {str(e)}", exc_info=True)
        flash('An error occurred while deleting the profile', 'danger')
        return redirect(url_for('view_database', slug=slug))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)