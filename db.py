# db.py - MongoDB Database Setup
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

# MongoDB connection
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb+srv://gcorporation04_db_user:oc8e32NtQc6Rjx9Q@cluster0.yzk9icp.mongodb.net/?appName=Cluster0")
DB_NAME = "career_guidance_db"

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Collection references
users_collection = db["users"]
sessions_collection = db["user_sessions"]
quiz_responses_collection = db["quiz_responses"]
recommendations_collection = db["career_recommendations"]
mentors_collection = db["mentors"]
mentor_connections_collection = db["mentor_connections"]
jobs_collection = db["job_opportunities"]

def init_db():
    """Initialize database indexes for optimal performance"""
    
    # Users collection indexes
    users_collection.create_index([("email", ASCENDING)], unique=True)
    users_collection.create_index([("username", ASCENDING)], unique=True)
    users_collection.create_index([("user_type", ASCENDING)])
    users_collection.create_index([("created_at", DESCENDING)])
    
    # User sessions collection indexes
    sessions_collection.create_index([("user_id", ASCENDING)])
    sessions_collection.create_index([("last_updated", DESCENDING)])
    
    # Quiz responses collection indexes
    quiz_responses_collection.create_index([("user_id", ASCENDING)])
    quiz_responses_collection.create_index([("quiz_type", ASCENDING)])
    quiz_responses_collection.create_index([("user_id", ASCENDING), ("quiz_type", ASCENDING)])
    quiz_responses_collection.create_index([("timestamp", DESCENDING)])
    
    # Career recommendations collection indexes
    recommendations_collection.create_index([("user_id", ASCENDING)])
    recommendations_collection.create_index([("career_path", ASCENDING)])
    recommendations_collection.create_index([("created_at", DESCENDING)])
    
    # Mentors collection indexes
    mentors_collection.create_index([("industry", ASCENDING)])
    mentors_collection.create_index([("expertise", ASCENDING)])
    mentors_collection.create_index([("industry", ASCENDING), ("expertise", ASCENDING)])
    
    # Mentor connections collection indexes
    mentor_connections_collection.create_index([("user_id", ASCENDING)])
    mentor_connections_collection.create_index([("mentor_id", ASCENDING)])
    mentor_connections_collection.create_index([("user_id", ASCENDING), ("mentor_id", ASCENDING)])
    mentor_connections_collection.create_index([("status", ASCENDING)])
    mentor_connections_collection.create_index([("created_at", DESCENDING)])
    
    # Job opportunities collection indexes
    jobs_collection.create_index([("industry", ASCENDING)])
    jobs_collection.create_index([("location", ASCENDING)])
    jobs_collection.create_index([("company", ASCENDING)])
    jobs_collection.create_index([("industry", ASCENDING), ("location", ASCENDING)])
    jobs_collection.create_index([("posted_at", DESCENDING)])
    
    print("MongoDB indexes created successfully!")

def get_db():
    """Returns the database instance"""
    return db

def create_default_users():
    """Create default user and mentor accounts if they don't exist"""
    try:
        # Check if default user exists
        if not users_collection.find_one({'username': 'user'}):
            user_doc = {
                'username': 'user',
                'email': 'user@example.com',
                'password_hash': generate_password_hash('password'),
                'name': 'Demo User',
                'user_type': 'user',
                'demographics': {
                    'skills': ['Programming', 'Analysis'],
                    'interests': 'Technology and Innovation',
                    'education': 'Bachelor\'s Degree',
                    'experience': '2 years',
                    'goals': 'Advance career in tech',
                    'location': 'New York, NY'
                },
                'created_at': datetime.utcnow()
            }
            users_collection.insert_one(user_doc)
            print("✓ Default user account created (username: user, password: password)")
        
        # Check if default mentor exists
        if not users_collection.find_one({'username': 'mentor'}):
            mentor_doc = {
                'username': 'mentor',
                'email': 'mentor@example.com',
                'password_hash': generate_password_hash('password'),
                'name': 'Demo Mentor',
                'user_type': 'mentor',
                'demographics': {
                    'skills': ['Leadership', 'Management', 'Mentoring'],
                    'interests': 'Helping others succeed',
                    'education': 'Master\'s Degree',
                    'experience': '10 years',
                    'industry': 'Technology',
                    'title': 'Senior Engineering Manager',
                    'company': 'Tech Corp',
                    'expertise': ['Software Engineering', 'Career Development', 'Technical Leadership'],
                    'bio': 'Experienced technology leader passionate about mentoring the next generation of tech professionals.',
                    'location': 'San Francisco, CA'
                },
                'created_at': datetime.utcnow()
            }
            users_collection.insert_one(mentor_doc)
            print("✓ Default mentor account created (username: mentor, password: password)")
    
    except Exception as e:
        print(f"Note: Default users may already exist or error occurred: {e}")

if __name__ == "__main__":
    init_db()
    create_default_users()
    print("Database initialized successfully!")