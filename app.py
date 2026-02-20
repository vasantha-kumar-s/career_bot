# app.py - Flask API with MongoDB, Gemini API, and Authentication
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import json
import datetime
import os
from db import (
    db, users_collection, sessions_collection, quiz_responses_collection,
    recommendations_collection, mentors_collection, mentor_connections_collection,
    jobs_collection, create_default_users
)

# Explicit Gemini API import with failure handling (API may be out of quota)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✓ Gemini API library loaded successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"⚠ Gemini API library not available: {e}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data.get('email', '')
        self.name = user_data.get('name', '')
        self.user_type = user_data.get('user_type', 'user')
        self.demographics = user_data.get('demographics', {})

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

# Configure Gemini API with explicit error handling
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
model = None

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✓ Gemini API configured successfully")
    except Exception as e:
        model = None
        print(f"⚠ Failed to configure Gemini API (expected when quota exceeded): {e}")
else:
    if not GEMINI_AVAILABLE:
        print("⚠ Gemini API library not imported - using fallback responses")
    elif not GEMINI_API_KEY:
        print("⚠ GEMINI_API_KEY not set - using fallback responses")

# Helper function to format chat history for Gemini
def format_chat_memory_as_text(chat_history):
    chat_history = chat_history[-20:]  # Limit memory to last 20 exchanges
    chat_text = []
    for msg in chat_history:
        role = "User" if msg.get('role') == 'user' else "Assistant"
        chat_text.append(f"{role}: {msg.get('content', '')}")
    return "\n".join(chat_text)

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    doc = dict(doc)
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime.datetime):
            doc[key] = value.isoformat()
    return doc

# ============= AUTHENTICATION ROUTES =============

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.user_type == 'mentor':
            return redirect(url_for('mentor_dashboard'))
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Find user by username
        user_data = users_collection.find_one({'username': username})
        
        if not user_data:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        # Check password
        if not check_password_hash(user_data['password_hash'], password):
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        # Create user object and log in
        user = User(user_data)
        login_user(user)
        
        # Determine redirect based on user type
        redirect_url = '/mentor-dashboard' if user.user_type == 'mentor' else '/home'
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect': redirect_url,
            'user_type': user.user_type
        })
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name', 'user_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.capitalize()} is required'}), 400
        
        # Check if username or email already exists
        if users_collection.find_one({'username': data['username']}):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if users_collection.find_one({'email': data['email']}):
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Create user document
        user_doc = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'name': data['name'],
            'user_type': data['user_type'],
            'demographics': {
                'skills': data.get('skills', []),
                'interests': data.get('interests', ''),
                'education': data.get('education', ''),
                'experience': data.get('experience', ''),
                'goals': data.get('goals', ''),
                'location': data.get('location', '')
            },
            'created_at': datetime.datetime.utcnow()
        }
        
        # Insert user
        result = users_collection.insert_one(user_doc)
        user_id = result.inserted_id
        
        # Save quiz responses if provided (from signup form)
        if data.get('skills') or data.get('interests'):
            quiz_doc = {
                'user_id': user_id,
                'responses': {
                    'skills': data.get('skills', []),
                    'interests': data.get('interests', ''),
                    'education': data.get('education', ''),
                    'experience': data.get('experience', ''),
                    'goals': data.get('goals', ''),
                    'location': data.get('location', '')
                },
                'timestamp': datetime.datetime.utcnow()
            }
            quiz_responses_collection.insert_one(quiz_doc)
        
        # Generate AI recommendations with explicit error handling
        recommendations = []
        try:
            if model:
                print("Attempting to generate AI recommendations for new user...")
                prompt = f"""Based on this user profile, suggest 3 career paths:
                Skills: {', '.join(data.get('skills', []))}
                Interests: {data.get('interests', '')}
                Education: {data.get('education', '')}
                Experience: {data.get('experience', '')}
                Goals: {data.get('goals', '')}
                
                Provide 3 career recommendations in JSON format with: career_path, description, match_score, skills."""
                
                response = model.generate_content(prompt)
                # Parse AI response (simplified - you may need more robust parsing)
                recommendations = [
                    {'career_path': 'AI-Generated Path 1', 'description': response.text[:200], 'match_score': 85}
                ]
                print("✓ AI recommendations generated successfully")
        except Exception as e:
            print(f"⚠ AI API call failed (expected when quota exceeded): {e}")
            # Fallback to default recommendations based on skills
            recommendations = generate_fallback_recommendations(data.get('skills', []), data.get('interests', ''))
        
        # Save recommendations
        if recommendations:
            for rec in recommendations:
                rec_doc = {
                    'user_id': user_id,
                    'career_path': rec.get('career_path', 'Career Path'),
                    'description': rec.get('description', 'No description available'),
                    'match_score': rec.get('match_score', 75),
                    'skills': rec.get('skills', []),
                    'timestamp': datetime.datetime.utcnow()
                }
                recommendations_collection.insert_one(rec_doc)
        
        # Log in the new user
        user_data = users_collection.find_one({'_id': user_id})
        user = User(user_data)
        login_user(user)
        
        redirect_url = '/mentor-dashboard' if user.user_type == 'mentor' else '/home'
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'redirect': redirect_url
        })
    
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during signup'}), 500

def generate_fallback_recommendations(skills, interests):
    """Generate fallback recommendations when AI is unavailable"""
    print("Generating fallback recommendations (AI unavailable)")
    recommendations = []
    
    # Simple rule-based recommendations
    if 'Programming' in skills or 'Analysis' in skills:
        recommendations.append({
            'career_path': 'Software Developer',
            'description': 'Build software applications and systems using programming languages and frameworks.',
            'match_score': 85,
            'skills': ['Programming', 'Problem Solving', 'Analysis']
        })
    
    if 'Design' in skills or 'Communication' in skills:
        recommendations.append({
            'career_path': 'UX/UI Designer',
            'description': 'Create user-friendly interfaces and experiences for digital products.',
            'match_score': 80,
            'skills': ['Design', 'Communication', 'Creativity']
        })
    
    if 'Leadership' in skills or 'Management' in skills:
        recommendations.append({
            'career_path': 'Project Manager',
            'description': 'Lead teams and manage projects to successful completion.',
            'match_score': 78,
            'skills': ['Leadership', 'Management', 'Communication']
        })
    
    # Default recommendation if no specific skills matched
    if not recommendations:
        recommendations.append({
            'career_path': 'Career Exploration',
            'description': 'Explore various career paths and develop your skills through courses and projects.',
            'match_score': 70,
            'skills': ['Learning', 'Adaptability']
        })
    
    return recommendations[:3]  # Return up to 3 recommendations

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    if current_user.user_type == 'mentor':
        return redirect(url_for('mentor_dashboard'))
    return render_template('dashboard.html')

@app.route('/mentor-dashboard')
@login_required
def mentor_dashboard():
    if current_user.user_type != 'mentor':
        return redirect(url_for('home'))
    return render_template('mentor_dashboard.html')

# ============= API ROUTES =============

@app.route('/api/current-user', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user information"""
    user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
    return jsonify(serialize_doc(user_data))

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400
        
        # Get user data for context
        user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
        demographics = user_data.get('demographics', {})
        
        # Get recent chat history
        recent_chats = list(sessions_collection.find({'user_id': ObjectId(current_user.id)})
                           .sort('timestamp', -1).limit(10))
        chat_history = [{'role': chat.get('role', 'user'), 'content': chat.get('message', '')} 
                       for chat in reversed(recent_chats)]
        
        # Build context prompt
        context = f"""User Profile:
        Name: {user_data.get('name', 'User')}
        Skills: {', '.join(demographics.get('skills', []))}
        Interests: {demographics.get('interests', 'Not specified')}
        Goals: {demographics.get('goals', 'Not specified')}
        
        Recent Conversation:
        {format_chat_memory_as_text(chat_history)}
        
        User's Question: {user_message}
        """
        
        response_text = ""
        
        # Try to get AI response with explicit error handling
        try:
            if model:
                print(f"Sending chat request to Gemini API...")
                prompt = f"""You are a career guidance counselor. Based on the context below, provide helpful career advice.
                
                {context}
                
                Provide a concise, helpful response focused on career guidance."""
                
                response = model.generate_content(prompt)
                response_text = response.text
                print("✓ AI response received successfully")
        except Exception as e:
            print(f"⚠ AI API call failed (expected when quota exceeded): {e}")
            # Fallback response
            response_text = """I'm here to help with your career journey! While I'm experiencing some technical limitations right now, I can still assist you with:

- Career path recommendations based on your skills and interests
- Guidance on skill development and education
- Job search strategies
- Resume and interview tips
- Connecting with mentors in your field

Could you tell me more specifically what aspect of your career you'd like to discuss?"""
        
        # Save chat messages to session history
        sessions_collection.insert_one({
            'user_id': ObjectId(current_user.id),
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.datetime.utcnow()
        })
        
        sessions_collection.insert_one({
            'user_id': ObjectId(current_user.id),
            'role': 'assistant',
            'message': response_text,
            'timestamp': datetime.datetime.utcnow()
        })
        
        return jsonify({'success': True, 'response': response_text})
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'response': 'Sorry, I encountered an error processing your message. Please try again.'
        }), 500

@app.route('/api/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get career recommendations for current user"""
    try:
        recs = list(recommendations_collection.find({'user_id': ObjectId(current_user.id)})
                   .sort('timestamp', -1).limit(10))
        
        # If no recommendations, try to generate some
        if not recs:
            user_data = users_collection.find_one({'_id': ObjectId(current_user.id)})
            demographics = user_data.get('demographics', {})
            
            try:
                if model:
                    print("Generating recommendations via AI...")
                    prompt = f"""Based on this profile, suggest 3 career paths:
                    Skills: {', '.join(demographics.get('skills', []))}
                    Interests: {demographics.get('interests', '')}
                    Goals: {demographics.get('goals', '')}
                    
                    Provide career recommendations with path name, description, and match score."""
                    
                    response = model.generate_content(prompt)
                    # For simplicity, create a basic recommendation from response
                    rec_doc = {
                        'user_id': ObjectId(current_user.id),
                        'career_path': 'AI-Generated Recommendation',
                        'description': response.text[:300],
                        'match_score': 85,
                        'skills': demographics.get('skills', []),
                        'timestamp': datetime.datetime.utcnow()
                    }
                    recommendations_collection.insert_one(rec_doc)
                    recs = [rec_doc]
                    print("✓ AI recommendations generated")
            except Exception as e:
                print(f"⚠ AI recommendation generation failed (expected): {e}")
                # Generate fallback recommendations
                fallback_recs = generate_fallback_recommendations(
                    demographics.get('skills', []),
                    demographics.get('interests', '')
                )
                for rec in fallback_recs:
                    rec_doc = {
                        'user_id': ObjectId(current_user.id),
                        'career_path': rec['career_path'],
                        'description': rec['description'],
                        'match_score': rec['match_score'],
                        'skills': rec['skills'],
                        'timestamp': datetime.datetime.utcnow()
                    }
                    recommendations_collection.insert_one(rec_doc)
                    recs.append(rec_doc)
        
        return jsonify({'success': True, 'recommendations': serialize_doc(recs)})
    
    except Exception as e:
        print(f"Recommendations error: {e}")
        return jsonify({'success': False, 'recommendations': []}), 500

@app.route('/api/mentors', methods=['GET'])
@login_required
def get_mentors():
    """Get list of mentors with optional filtering"""
    try:
        industry = request.args.get('industry', '').strip()
        expertise = request.args.get('expertise', '').strip()
        
        query = {}
        if industry and industry != 'all':
            query['industry'] = industry
        if expertise:
            query['expertise'] = {'$in': [expertise]}
        
        mentors = list(mentors_collection.find(query).limit(50))
        return jsonify({'success': True, 'mentors': serialize_doc(mentors)})
    
    except Exception as e:
        print(f"Mentors error: {e}")
        return jsonify({'success': False, 'mentors': []}), 500

@app.route('/api/mentor-connection', methods=['POST'])
@login_required
def request_mentor_connection():
    """Request connection with a mentor"""
    try:
        data = request.get_json()
        mentor_id = data.get('mentor_id', '').strip()
        message = data.get('message', '').strip()
        
        if not mentor_id:
            return jsonify({'success': False, 'message': 'Mentor ID required'}), 400
        
        # Check if mentor exists
        mentor = mentors_collection.find_one({'_id': ObjectId(mentor_id)})
        if not mentor:
            return jsonify({'success': False, 'message': 'Mentor not found'}), 404
        
        # Check if connection already exists
        existing = mentor_connections_collection.find_one({
            'user_id': ObjectId(current_user.id),
            'mentor_id': ObjectId(mentor_id)
        })
        
        if existing:
            return jsonify({'success': False, 'message': 'Connection request already exists'}), 400
        
        # Create connection request
        connection_doc = {
            'user_id': ObjectId(current_user.id),
            'user_name': current_user.name,
            'user_email': current_user.email,
            'mentor_id': ObjectId(mentor_id),
            'mentor_name': mentor.get('name', ''),
            'message': message,
            'status': 'pending',
            'timestamp': datetime.datetime.utcnow()
        }
        
        mentor_connections_collection.insert_one(connection_doc)
        
        return jsonify({'success': True, 'message': 'Connection request sent successfully'})
    
    except Exception as e:
        print(f"Mentor connection error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send connection request'}), 500

@app.route('/api/jobs', methods=['GET'])
@login_required
def get_jobs():
    """Get job opportunities with optional filtering"""
    try:
        industry = request.args.get('industry', '').strip()
        location = request.args.get('location', '').strip()
        
        query = {}
        if industry and industry != 'all':
            query['industry'] = industry
        if location:
            query['location'] = {'$regex': location, '$options': 'i'}
        
        jobs = list(jobs_collection.find(query).limit(50))
        return jsonify({'success': True, 'jobs': serialize_doc(jobs)})
    
    except Exception as e:
        print(f"Jobs error: {e}")
        return jsonify({'success': False, 'jobs': []}), 500

# ============= MENTOR-SPECIFIC ROUTES =============

@app.route('/api/mentor-stats', methods=['GET'])
@login_required
def get_mentor_stats():
    """Get mentor statistics (for mentor dashboard)"""
    try:
        if current_user.user_type != 'mentor':
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        # Count connections
        total_connections = mentor_connections_collection.count_documents({
            'mentor_id': ObjectId(current_user.id),
            'status': 'accepted'
        })
        
        pending_requests = mentor_connections_collection.count_documents({
            'mentor_id': ObjectId(current_user.id),
            'status': 'pending'
        })
        
        return jsonify({
            'success': True,
            'total_connections': total_connections,
            'pending_requests': pending_requests,
            'total_messages': 0,  # Placeholder
            'avg_rating': 5.0  # Placeholder
        })
    
    except Exception as e:
        print(f"Mentor stats error: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/mentor-requests', methods=['GET'])
@login_required
def get_mentor_requests():
    """Get pending mentor connection requests"""
    try:
        if current_user.user_type != 'mentor':
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        requests = list(mentor_connections_collection.find({
            'mentor_id': ObjectId(current_user.id),
            'status': 'pending'
        }).sort('timestamp', -1))
        
        return jsonify({'success': True, 'requests': serialize_doc(requests)})
    
    except Exception as e:
        print(f"Mentor requests error: {e}")
        return jsonify({'success': False, 'requests': []}), 500

@app.route('/api/mentor-mentees', methods=['GET'])
@login_required
def get_mentor_mentees():
    """Get list of accepted mentees"""
    try:
        if current_user.user_type != 'mentor':
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        mentees = list(mentor_connections_collection.find({
            'mentor_id': ObjectId(current_user.id),
            'status': 'accepted'
        }).sort('timestamp', -1))
        
        return jsonify({'success': True, 'mentees': serialize_doc(mentees)})
    
    except Exception as e:
        print(f"Mentor mentees error: {e}")
        return jsonify({'success': False, 'mentees': []}), 500

@app.route('/api/mentor-accept', methods=['POST'])
@login_required
def accept_mentor_request():
    """Accept a mentor connection request"""
    try:
        if current_user.user_type != 'mentor':
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        data = request.get_json()
        request_id = data.get('request_id', '').strip()
        
        if not request_id:
            return jsonify({'success': False, 'message': 'Request ID required'}), 400
        
        result = mentor_connections_collection.update_one(
            {'_id': ObjectId(request_id), 'mentor_id': ObjectId(current_user.id)},
            {'$set': {'status': 'accepted', 'accepted_at': datetime.datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Request accepted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
    
    except Exception as e:
        print(f"Accept request error: {e}")
        return jsonify({'success': False, 'message': 'Failed to accept request'}), 500

@app.route('/api/mentor-reject', methods=['POST'])
@login_required
def reject_mentor_request():
    """Reject a mentor connection request"""
    try:
        if current_user.user_type != 'mentor':
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        data = request.get_json()
        request_id = data.get('request_id', '').strip()
        
        if not request_id:
            return jsonify({'success': False, 'message': 'Request ID required'}), 400
        
        result = mentor_connections_collection.update_one(
            {'_id': ObjectId(request_id), 'mentor_id': ObjectId(current_user.id)},
            {'$set': {'status': 'rejected', 'rejected_at': datetime.datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Request rejected'})
        else:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
    
    except Exception as e:
        print(f"Reject request error: {e}")
        return jsonify({'success': False, 'message': 'Failed to reject request'}), 500

if __name__ == '__main__':
    # Create default users (user/password and mentor/password)
    create_default_users()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
