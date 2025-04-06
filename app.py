# app.py - Flask API
from flask import Flask, request, jsonify, render_template
from sqlalchemy.orm import Session
import json
import datetime
import google.generativeai as genai
import os
from db import SessionLocal, User, UserSession, QuizResponse, CareerRecommendation, Mentor, MentorConnection, JobOpportunity
from functools import lru_cache
from contextlib import contextmanager

app = Flask(__name__)

# Configure Gemini API key
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash-lite')

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Cache the system prompt to avoid string reconstruction on every request
SYSTEM_PROMPT = """
You are a career guidance chatbot that helps users with career planning, skill development, 
and job search. You have access to the user's profile information, their quiz responses, 
and can suggest career paths, mentors, and job opportunities based on their interests and skills.

Always be supportive, encouraging, and provide personalized guidance. If you don't have enough
information about the user, ask relevant questions to build their profile. Format your responses
in a clear, structured way.
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/user', methods=['POST'])
def create_user():
    with get_db() as db:
        data = request.json
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == data.get('email')).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists", "user_id": existing_user.user_id})
        
        # Create new user
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            demographics=json.dumps(data.get('demographics', {}))
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return jsonify({"message": "User created successfully", "user_id": new_user.user_id})

@app.route('/api/chat', methods=['POST'])
def chat():
    with get_db() as db:
        data = request.json
        user_id = data.get('user_id')
        user_message = data.get('message')

        # Get user
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get or create user session
        session = db.query(UserSession).filter(UserSession.user_id == user_id).first()
        if not session:
            session = UserSession(user_id=user_id, conversation_history=json.dumps([]))
            db.add(session)
            db.commit()
            db.refresh(session)

        # Get and format chat history
        chat_history = json.loads(session.conversation_history or "[]")
        chat_memory = format_chat_memory_as_text(chat_history)

        # Prepare user context - using more efficient querying
        quiz_responses = db.query(QuizResponse).filter(QuizResponse.user_id == user_id).all()
        
        # Only fetch career recommendations if we have quiz responses
        career_recommendations = []
        if quiz_responses:
            career_recommendations = db.query(CareerRecommendation).filter(CareerRecommendation.user_id == user_id).all()
        
        # Use a join to get mentor information in a single query
        mentor_info = []
        mentor_connections = db.query(MentorConnection, Mentor).join(
            Mentor, MentorConnection.mentor_id == Mentor.mentor_id
        ).filter(
            MentorConnection.user_id == user_id,
            MentorConnection.status == "connected"
        ).all()
        
        for connection, mentor in mentor_connections:
            mentor_info.append({
                "name": mentor.name,
                "industry": mentor.industry,
                "expertise": mentor.expertise
            })
        
        # Get recent job opportunities that match user's interests - limit DB query
        user_interests = [q.answer for q in quiz_responses if q.quiz_type == "interests"]
        relevant_jobs = []
        if user_interests:
            # Get jobs that might match user interests - limited to 5 most recent
            jobs = db.query(JobOpportunity).order_by(JobOpportunity.posted_at.desc()).limit(5).all()
            relevant_jobs = [{
                "title": job.title,
                "company": job.company,
                "industry": job.industry,
                "location": job.location
            } for job in jobs]

        # Build user context object
        user_context = {
            "name": user.name,
            "demographics": json.loads(user.demographics) if user.demographics else {},
            "quiz_responses": [{"question": q.question, "answer": q.answer, "type": q.quiz_type} for q in quiz_responses],
            "recommendations": [{"career": r.career_path, "text": r.recommendation_text} for r in career_recommendations],
            "mentors": mentor_info,
            "relevant_jobs": relevant_jobs,
            "current_date": "Sunday, April 06, 2025, 5:45 PM IST"
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

        # Call Gemini model
        response = model.generate_content(final_prompt)
        response_text = response.text.strip()

        # Only process potential skill/interest extraction if the message is likely to contain them
        # This avoids redundant database operations
        if any(keyword in user_message.lower() for keyword in ["my skill", "i am good at", "i like", "my interest", "i enjoy"]):
            # Extract potential quiz data
            quiz_type = "skills" if any(k in user_message.lower() for k in ["skill", "good at", "can do"]) else "interests"
            
            # Save as a quiz response
            new_quiz = QuizResponse(
                user_id=user_id,
                question=f"Information extracted from chat about {quiz_type}",
                answer=user_message,
                quiz_type=quiz_type
            )
            db.add(new_quiz)
            db.commit()

        # Update chat history efficiently
        new_history = chat_history + [
            {"role": "user", "parts": [user_message]},
            {"role": "model", "parts": [response_text]}
        ]

        # Save updated chat history
        session.conversation_history = json.dumps(new_history)
        session.last_updated = datetime.datetime.utcnow()
        db.commit()

        return jsonify({"response": response_text})

@app.route('/api/quiz', methods=['POST'])
def save_quiz():
    with get_db() as db:
        data = request.json
        user_id = data.get('user_id')
        question = data.get('question')
        answer = data.get('answer')
        quiz_type = data.get('quiz_type', 'general')
        
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Save quiz response
        quiz_response = QuizResponse(
            user_id=user_id,
            question=question,
            answer=answer,
            quiz_type=quiz_type
        )
        
        db.add(quiz_response)
        db.commit()
        
        return jsonify({"status": "success", "message": "Quiz response saved"})

@lru_cache(maxsize=128)
def get_cached_recommendations(user_id, cache_key):
    """Cache recommendations to reduce database load"""
    with get_db() as db:
        existing_recs = db.query(CareerRecommendation).filter(CareerRecommendation.user_id == user_id).all()
        recommendations = [
            {
                "id": rec.recommendation_id,
                "career_path": rec.career_path,
                "text": rec.recommendation_text,
                "confidence": rec.confidence_score,
                "created_at": rec.created_at.isoformat()
            }
            for rec in existing_recs
        ]
        return recommendations

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('user_id')
    cache_key = f"user_recommendations_{user_id}"
    
    with get_db() as db:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get quiz responses
        quiz_responses = db.query(QuizResponse).filter(QuizResponse.user_id == user_id).all()
        if not quiz_responses:
            return jsonify({"error": "No quiz responses found for this user"}), 404
        
        # Get existing recommendations
        existing_recs = db.query(CareerRecommendation).filter(CareerRecommendation.user_id == user_id).all()
        
        # If recommendations exist, return them
        if existing_recs:
            # Use cached results if available
            recommendations = get_cached_recommendations(user_id, cache_key)
            return jsonify({"recommendations": recommendations})
        
        # Otherwise, generate new recommendations using Gemini
        # Prepare quiz data for the LLM
        quiz_data = [
            {
                "question": q.question,
                "answer": q.answer,
                "type": q.quiz_type
            }
            for q in quiz_responses
        ]
        
        # Create prompt for Gemini
        recommendation_prompt = f"""
        Based on the following quiz responses from {user.name}, suggest 3 possible career paths.
        For each career path, provide:
        1. The name of the career path
        2. A brief explanation of why it's a good fit (3-5 sentences)
        3. A confidence score (0-100)
        
        Quiz responses:
        {json.dumps(quiz_data, indent=2)}
        
        Format your response as a JSON array with objects containing the fields: career_path, explanation, confidence_score
        """
        
        # Get recommendations from Gemini
        response = model.generate_content(recommendation_prompt)
        
        try:
            # Parse the response and extract the recommendations
            recommendations_json = json.loads(response.text)
            
            # Batch add recommendations for better performance
            recommendations_to_add = []
            for rec in recommendations_json:
                new_rec = CareerRecommendation(
                    user_id=user_id,
                    career_path=rec["career_path"],
                    recommendation_text=rec["explanation"],
                    confidence_score=rec["confidence_score"]
                )
                recommendations_to_add.append(new_rec)
            
            if recommendations_to_add:
                db.bulk_save_objects(recommendations_to_add)
                db.commit()
            
            # Fetch the newly created recommendations with their IDs
            new_recs = db.query(CareerRecommendation).filter(CareerRecommendation.user_id == user_id).all()
            recommendations = [
                {
                    "id": rec.recommendation_id,
                    "career_path": rec.career_path,
                    "text": rec.recommendation_text,
                    "confidence": rec.confidence_score,
                    "created_at": rec.created_at.isoformat()
                }
                for rec in new_recs
            ]
            
            # Invalidate the cache key
            get_cached_recommendations.cache_clear()
            
            return jsonify({"recommendations": recommendations})
        
        except Exception as e:
            return jsonify({"error": f"Error generating recommendations: {str(e)}"}), 500

@app.route('/api/mentors', methods=['GET'])
def get_mentors():
    with get_db() as db:
        industry = request.args.get('industry')
        expertise = request.args.get('expertise')
        
        # Build query for mentors
        query = db.query(Mentor)
        
        # Apply filters if provided
        if industry:
            query = query.filter(Mentor.industry == industry)
        if expertise:
            query = query.filter(Mentor.expertise == expertise)
        
        mentors = query.all()
        
        # Format mentor data
        mentor_list = [
            {
                "id": mentor.mentor_id,
                "name": mentor.name,
                "industry": mentor.industry,
                "expertise": mentor.expertise,
                "experience_years": mentor.experience_years,
                "availability": json.loads(mentor.availability) if mentor.availability else {}
            }
            for mentor in mentors
        ]
        
        return jsonify({"mentors": mentor_list})

@app.route('/api/mentor-connection', methods=['POST'])
def create_mentor_connection():
    with get_db() as db:
        data = request.json
        user_id = data.get('user_id')
        mentor_id = data.get('mentor_id')
        
        # Use a single query to validate both user and mentor exist
        user_exists = db.query(User).filter(User.user_id == user_id).first() is not None
        mentor_exists = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first() is not None
        
        if not user_exists:
            return jsonify({"error": "User not found"}), 404
        if not mentor_exists:
            return jsonify({"error": "Mentor not found"}), 404
        
        # Check if connection already exists
        existing_connection = db.query(MentorConnection).filter(
            MentorConnection.user_id == user_id,
            MentorConnection.mentor_id == mentor_id
        ).first()
        
        if existing_connection:
            return jsonify({"error": "Connection already exists", "status": existing_connection.status}), 400
        
        # Create new connection
        connection = MentorConnection(
            user_id=user_id,
            mentor_id=mentor_id,
            status="pending"
        )
        
        db.add(connection)
        db.commit()
        
        return jsonify({"status": "success", "message": "Mentor connection request sent"})

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    with get_db() as db:
        industry = request.args.get('industry')
        location = request.args.get('location')
        
        # Build more efficient query for jobs
        query = db.query(
            JobOpportunity.job_id,
            JobOpportunity.title,
            JobOpportunity.company,
            JobOpportunity.description,
            JobOpportunity.industry,
            JobOpportunity.location,
            JobOpportunity.salary_range,
            JobOpportunity.requirements,
            JobOpportunity.posted_at
        )
        
        # Apply filters if provided
        if industry:
            query = query.filter(JobOpportunity.industry == industry)
        if location:
            query = query.filter(JobOpportunity.location == location)
        
        # Get most recent jobs, limit to 20
        jobs = query.order_by(JobOpportunity.posted_at.desc()).limit(20).all()
        
        # Format job data
        job_list = [
            {
                "id": job.job_id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "industry": job.industry,
                "location": job.location,
                "salary_range": job.salary_range,
                "requirements": job.requirements,
                "posted_at": job.posted_at.isoformat()
            }
            for job in jobs
        ]
        
        return jsonify({"jobs": job_list})

if __name__ == '__main__':
    app.run(debug=True)
