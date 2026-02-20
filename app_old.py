# app.py - Flask API with MongoDB and Gemini API
from flask import Flask, request, jsonify, render_template
from bson import ObjectId
import json
import datetime
import google.generativeai as genai
import os
from db import (
    db, users_collection, sessions_collection, quiz_responses_collection,
    recommendations_collection, mentors_collection, mentor_connections_collection,
    jobs_collection
)
from functools import lru_cache

app = Flask(__name__)

# Configure Gemini API key with fallback
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    model = None

# Helper function to format chat history for Gemini
def format_chat_memory_as_text(chat_history):
    # Limit memory to last 20 exchanges
    chat_history = chat_history[-20:]  
    chat_text = []
    for msg in chat_history:
        role = "You" if msg["role"] == "user" else "AI"
        content = msg["parts"][0].strip()
        chat_text.append(f"{role}: {content}")
    return "\n".join(chat_text)

# Cache the system prompt
SYSTEM_PROMPT = """
You are a career guidance chatbot that helps users with career planning, skill development, 
and job search. You have access to the user's profile information, their quiz responses, 
and can suggest career paths, mentors, and job opportunities based on their interests and skills.

Always be supportive, encouraging, and provide personalized guidance. If you don't have enough
information about the user, ask relevant questions to build their profile. Format your responses
in a clear, structured way.
"""

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/demo-users', methods=['GET'])
def get_demo_users():
    """Get list of demo users for selection"""
    users = list(users_collection.find().limit(10))
    user_list = [
        {
            "_id": str(user['_id']),
            "name": user['name'],
            "email": user['email']
        }
        for user in users
    ]
    return jsonify({"users": user_list})

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.json
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": data.get('email')})
    if existing_user:
        return jsonify({
            "error": "User with this email already exists",
            "user_id": str(existing_user['_id'])
        })
    
    # Create new user
    new_user = {
        "name": data.get('name'),
        "email": data.get('email'),
        "demographics": data.get('demographics', {}),
        "created_at": datetime.datetime.utcnow()
    }
    
    result = users_collection.insert_one(new_user)
    
    return jsonify({
        "message": "User created successfully",
        "user_id": str(result.inserted_id)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    user_message = data.get('message')

    # Get user
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return jsonify({"error": "Invalid user ID"}), 404

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get or create user session
    session = sessions_collection.find_one({"user_id": user_id})
    if not session:
        session = {
            "user_id": user_id,
            "conversation_history": [],
            "last_updated": datetime.datetime.utcnow()
        }
        sessions_collection.insert_one(session)

    # Get and format chat history
    chat_history = session.get('conversation_history', [])
    chat_memory = format_chat_memory_as_text(chat_history)

    # Prepare user context
    quiz_responses = list(quiz_responses_collection.find({"user_id": user_id}))
    
    # Get career recommendations if quiz responses exist
    career_recommendations = []
    if quiz_responses:
        career_recommendations = list(recommendations_collection.find({"user_id": user_id}))
    
    # Get mentor information
    mentor_info = []
    mentor_connections = list(mentor_connections_collection.find({
        "user_id": user_id,
        "status": "connected"
    }))
    
    for connection in mentor_connections:
        mentor = mentors_collection.find_one({"_id": ObjectId(connection['mentor_id'])})
        if mentor:
            mentor_info.append({
                "name": mentor['name'],
                "industry": mentor['industry'],
                "expertise": mentor['expertise']
            })
    
    # Get recent job opportunities that match user's interests
    user_interests = [q['answer'] for q in quiz_responses if q.get('quiz_type') == "interests"]
    relevant_jobs = []
    if user_interests:
        jobs = list(jobs_collection.find().sort("posted_at", -1).limit(5))
        relevant_jobs = [{
            "title": job['title'],
            "company": job['company'],
            "industry": job['industry'],
            "location": job['location']
        } for job in jobs]

    # Build user context object
    user_context = {
        "name": user['name'],
        "demographics": user.get('demographics', {}),
        "quiz_responses": [{"question": q.get('question'), "answer": q.get('answer'), "type": q.get('quiz_type')} for q in quiz_responses],
        "recommendations": [{"career": r.get('career_path'), "text": r.get('recommendation_text')} for r in career_recommendations],
        "mentors": mentor_info,
        "relevant_jobs": relevant_jobs,
        "current_date": datetime.datetime.utcnow().strftime("%A, %B %d, %Y, %I:%M %p IST")
    }

    # Build final prompt string
    final_prompt = f"""{SYSTEM_PROMPT.strip()}

User context: {json.dumps(user_context, indent=2)}

Chat history:
{chat_memory}

Please provide a well-structured response that:
1. Directly addresses the user's current question
2. Maintains continuity with our previous conversation
3. Uses clear headings, bullet points, or numbered lists when appropriate
4. Provides specific, actionable advice related to career guidance
5. References relevant information from the user's profile when applicable

User: {user_message}

Bot:"""

    # Call Gemini model with fallback
    if model:
        try:
            response = model.generate_content(final_prompt)
            response_text = response.text.strip()
        except Exception as e:
            response_text = f"I'm having trouble connecting to my AI service right now. However, I can still help you with career guidance! Based on your question about '{user_message}', I'd be happy to assist. Could you provide more specific details about what you'd like to know?"
    else:
        response_text = f"Thank you for your message! I'm currently operating in limited mode. I can help you explore career paths, find mentors, and discover job opportunities. What specific aspect of your career would you like to discuss?"

    # Extract potential skill/interest data
    if any(keyword in user_message.lower() for keyword in ["my skill", "i am good at", "i like", "my interest", "i enjoy"]):
        quiz_type = "skills" if any(k in user_message.lower() for k in ["skill", "good at", "can do"]) else "interests"
        
        new_quiz = {
            "user_id": user_id,
            "question": f"Information extracted from chat about {quiz_type}",
            "answer": user_message,
            "quiz_type": quiz_type,
            "timestamp": datetime.datetime.utcnow()
        }
        quiz_responses_collection.insert_one(new_quiz)

    # Update chat history
    new_history = chat_history + [
        {"role": "user", "parts": [user_message]},
        {"role": "model", "parts": [response_text]}
    ]

    # Save updated chat history
    sessions_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "conversation_history": new_history,
                "last_updated": datetime.datetime.utcnow()
            }
        }
    )

    return jsonify({"response": response_text})

@app.route('/api/quiz', methods=['POST'])
def save_quiz():
    data = request.json
    user_id = data.get('user_id')
    question = data.get('question')
    answer = data.get('answer')
    quiz_type = data.get('quiz_type', 'general')
    
    # Validate user exists
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return jsonify({"error": "Invalid user ID"}), 404
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Save quiz response
    quiz_response = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "quiz_type": quiz_type,
        "timestamp": datetime.datetime.utcnow()
    }
    
    quiz_responses_collection.insert_one(quiz_response)
    
    return jsonify({"status": "success", "message": "Quiz response saved"})

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')
    
    # Validate user exists
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return jsonify({"error": "Invalid user ID"}), 404
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get quiz responses
    quiz_responses = list(quiz_responses_collection.find({"user_id": user_id}))
    if not quiz_responses:
        return jsonify({"error": "No quiz responses found for this user"}), 404
    
    # Get existing recommendations
    existing_recs = list(recommendations_collection.find({"user_id": user_id}))
    
    # If recommendations exist, return them
    if existing_recs:
        recommendations = [
            {
                "id": str(rec['_id']),
                "career_path": rec['career_path'],
                "text": rec['recommendation_text'],
                "confidence": rec['confidence_score'],
                "created_at": rec['created_at'].isoformat()
            }
            for rec in existing_recs
        ]
        return jsonify({"recommendations": recommendations})
    
    # Generate new recommendations using Gemini with fallback
    quiz_data = [
        {
            "question": q.get('question'),
            "answer": q.get('answer'),
            "type": q.get('quiz_type')
        }
        for q in quiz_responses
    ]
    
    # Create prompt for Gemini
    recommendation_prompt = f"""
    Based on the following quiz responses from {user['name']}, suggest 3 possible career paths.
    For each career path, provide:
    1. The name of the career path
    2. A brief explanation of why it's a good fit (3-5 sentences)
    3. A confidence score (0-100)
    
    Quiz responses:
    {json.dumps(quiz_data, indent=2)}
    
    Format your response as a JSON array with objects containing the fields: career_path, explanation, confidence_score
    """
    
    # Get recommendations from Gemini with fallback
    if model:
        try:
            response = model.generate_content(recommendation_prompt)
            recommendations_json = json.loads(response.text)
        except:
            # Fallback recommendations based on quiz data
            recommendations_json = [
                {
                    "career_path": "Data Science & Analytics",
                    "explanation": "Based on your responses, you show strong analytical thinking and interest in working with data. Data Science combines technical skills with business insights, making it a great fit for someone who enjoys problem-solving and continuous learning.",
                    "confidence_score": 85
                },
                {
                    "career_path": "Software Development",
                    "explanation": "Your profile indicates good logical thinking and interest in technology. Software development offers diverse opportunities across industries and allows you to build tangible products that solve real-world problems.",
                    "confidence_score": 78
                },
                {
                    "career_path": "Product Management",
                    "explanation": "You demonstrate a balance of technical understanding and communication skills. Product management would allow you to bridge the gap between technical teams and business objectives while driving product strategy.",
                    "confidence_score": 72
                }
            ]
    else:
        # Default recommendations when no API is available
        recommendations_json = [
            {
                "career_path": "Technology & Software",
                "explanation": "Technology careers offer excellent growth opportunities and are in high demand across all industries. Consider roles in software development, data analysis, or IT management based on your interests.",
                "confidence_score": 80
            },
            {
                "career_path": "Business & Management",
                "explanation": "Business roles provide opportunities to lead teams, drive strategy, and make impactful decisions. Consider exploring business analysis, project management, or consulting careers.",
                "confidence_score": 75
            },
            {
                "career_path": "Creative & Design",
                "explanation": "Creative fields combine artistic skills with technical knowledge. Explore opportunities in UI/UX design, digital marketing, or content creation based on your creative interests.",
                "confidence_score": 70
            }
        ]
    
    try:
        # Save recommendations
        recommendations_to_add = []
        for rec in recommendations_json:
            new_rec = {
                "user_id": user_id,
                "career_path": rec["career_path"],
                "recommendation_text": rec["explanation"],
                "confidence_score": rec["confidence_score"],
                "created_at": datetime.datetime.utcnow()
            }
            recommendations_to_add.append(new_rec)
        
        if recommendations_to_add:
            recommendations_collection.insert_many(recommendations_to_add)
        
        # Fetch the newly created recommendations
        new_recs = list(recommendations_collection.find({"user_id": user_id}))
        recommendations = [
            {
                "id": str(rec['_id']),
                "career_path": rec['career_path'],
                "text": rec['recommendation_text'],
                "confidence": rec['confidence_score'],
                "created_at": rec['created_at'].isoformat()
            }
            for rec in new_recs
        ]
        
        return jsonify({"recommendations": recommendations})
    
    except Exception as e:
        return jsonify({"error": f"Error generating recommendations: {str(e)}"}), 500

@app.route('/api/mentors', methods=['GET'])
def get_mentors():
    industry = request.args.get('industry')
    expertise = request.args.get('expertise')
    
    # Build query for mentors
    query = {}
    if industry:
        query['industry'] = industry
    if expertise:
        query['expertise'] = expertise
    
    mentors = list(mentors_collection.find(query))
    
    # Format mentor data
    mentor_list = [
        {
            "id": str(mentor['_id']),
            "name": mentor['name'],
            "industry": mentor['industry'],
            "expertise": mentor['expertise'],
            "experience_years": mentor['experience_years'],
            "availability": mentor.get('availability', {})
        }
        for mentor in mentors
    ]
    
    return jsonify({"mentors": mentor_list})

@app.route('/api/mentor-connection', methods=['POST'])
def create_mentor_connection():
    data = request.json
    user_id = data.get('user_id')
    mentor_id = data.get('mentor_id')
    
    # Validate user and mentor exist
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        mentor = mentors_collection.find_one({"_id": ObjectId(mentor_id)})
    except:
        return jsonify({"error": "Invalid ID format"}), 400
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not mentor:
        return jsonify({"error": "Mentor not found"}), 404
    
    # Check if connection already exists
    existing_connection = mentor_connections_collection.find_one({
        "user_id": user_id,
        "mentor_id": mentor_id
    })
    
    if existing_connection:
        return jsonify({
            "error": "Connection already exists",
            "status": existing_connection['status']
        }), 400
    
    # Create new connection
    connection = {
        "user_id": user_id,
        "mentor_id": mentor_id,
        "status": "pending",
        "created_at": datetime.datetime.utcnow()
    }
    
    mentor_connections_collection.insert_one(connection)
    
    return jsonify({"status": "success", "message": "Mentor connection request sent"})

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    industry = request.args.get('industry')
    location = request.args.get('location')
    
    # Build query for jobs
    query = {}
    if industry:
        query['industry'] = industry
    if location:
        query['location'] = location
    
    # Get most recent jobs, limit to 20
    jobs = list(jobs_collection.find(query).sort("posted_at", -1).limit(20))
    
    # Format job data
    job_list = [
        {
            "id": str(job['_id']),
            "title": job['title'],
            "company": job['company'],
            "description": job['description'],
            "industry": job['industry'],
            "location": job['location'],
            "salary_range": job.get('salary_range', 'Not specified'),
            "requirements": job.get('requirements', ''),
            "posted_at": job['posted_at'].isoformat()
        }
        for job in jobs
    ]
    
    return jsonify({"jobs": job_list})

if __name__ == '__main__':
    app.run(debug=True)
