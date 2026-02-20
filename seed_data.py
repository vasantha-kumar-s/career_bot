# Migrated to MongoDB
# seed_data.py - Seed MongoDB with demo data
from db import (
    init_db, users_collection, mentors_collection, jobs_collection,
    quiz_responses_collection, recommendations_collection, sessions_collection
)
import json
import datetime

def seed_database():
    """Seed the database with demo data for testing"""
    
    # Initialize the database indexes
    init_db()
    
    # Check if data already exists
    if users_collection.count_documents({}) > 0:
        print("Database is already seeded.")
        response = input("Do you want to clear and re-seed? (yes/no): ")
        if response.lower() != 'yes':
            return
        
        # Clear existing data
        users_collection.delete_many({})
        sessions_collection.delete_many({})
        quiz_responses_collection.delete_many({})
        recommendations_collection.delete_many({})
        mentors_collection.delete_many({})
        jobs_collection.delete_many({})
        print("Existing data cleared.")
    
    # Current date for reference
    current_date = datetime.datetime(2026, 2, 20)
    
    # Seed demo users
    demo_users = [
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "demographics": {
                "age": 22,
                "location": "Mumbai, India",
                "education": "B.Tech Computer Science",
                "current_status": "Final Year Student"
            },
            "created_at": current_date - datetime.timedelta(days=30)
        },
        {
            "name": "Rahul Verma",
            "email": "rahul.verma@example.com",
            "demographics": {
                "age": 24,
                "location": "Bangalore, India",
                "education": "MBA",
                "current_status": "Working Professional"
            },
            "created_at": current_date - datetime.timedelta(days=15)
        },
        {
            "name": "Ananya Reddy",
            "email": "ananya.reddy@example.com",
            "demographics": {
                "age": 21,
                "location": "Hyderabad, India",
                "education": "B.Des Design",
                "current_status": "Recent Graduate"
            },
            "created_at": current_date - datetime.timedelta(days=7)
        }
    ]
    
    print("Seeding demo users...")
    user_results = users_collection.insert_many(demo_users)
    user_ids = [str(uid) for uid in user_results.inserted_ids]
    print(f"✓ Added {len(user_ids)} demo users")
    
    # Add sample quiz responses for demo users
    print("Adding sample quiz responses...")
    demo_quiz_responses = [
        # Priya's responses
        {
            "user_id": user_ids[0],
            "question": "What are your key skills?",
            "answer": "Python programming, data analysis, machine learning, problem-solving",
            "quiz_type": "skills",
            "timestamp": current_date - datetime.timedelta(days=25)
        },
        {
            "user_id": user_ids[0],
            "question": "What are your career interests?",
            "answer": "I'm interested in data science, artificial intelligence, and building intelligent systems",
            "quiz_type": "interests",
            "timestamp": current_date - datetime.timedelta(days=25)
        },
        {
            "user_id": user_ids[0],
            "question": "What is your work experience?",
            "answer": "2 internships in data analytics, personal projects in ML",
            "quiz_type": "experience",
            "timestamp": current_date - datetime.timedelta(days=25)
        },
        # Rahul's responses
        {
            "user_id": user_ids[1],
            "question": "What are your key skills?",
            "answer": "Business strategy, market analysis, project management, leadership",
            "quiz_type": "skills",
            "timestamp": current_date - datetime.timedelta(days=12)
        },
        {
            "user_id": user_ids[1],
            "question": "What are your career interests?",
            "answer": "Product management, business consulting, startup ecosystem",
            "quiz_type": "interests",
            "timestamp": current_date - datetime.timedelta(days=12)
        },
        # Ananya's responses
        {
            "user_id": user_ids[2],
            "question": "What are your key skills?",
            "answer": "UI/UX design, Figma, Adobe XD, user research, prototyping",
            "quiz_type": "skills",
            "timestamp": current_date - datetime.timedelta(days=5)
        },
        {
            "user_id": user_ids[2],
            "question": "What are your career interests?",
            "answer": "UX design, product design, design systems, user experience research",
            "quiz_type": "interests",
            "timestamp": current_date - datetime.timedelta(days=5)
        }
    ]
    
    quiz_responses_collection.insert_many(demo_quiz_responses)
    print(f"✓ Added {len(demo_quiz_responses)} quiz responses")
    
    # Seed mentors with diverse expertise
    print("Seeding mentors...")
    mentors = [
        # Technology Mentors
        {
            "name": "Ruchi Chauhan",
            "industry": "technology",
            "expertise": "Data Science",
            "experience_years": 6,
            "availability": {
                "monday": ["10:00-12:00", "14:00-16:00"],
                "wednesday": ["10:00-12:00"],
                "friday": ["14:00-16:00"]
            }
        },
        {
            "name": "Syed Quiser Ahmed",
            "industry": "technology",
            "expertise": "Responsible AI",
            "experience_years": 15,
            "availability": {
                "tuesday": ["13:00-15:00"],
                "thursday": ["10:00-12:00"]
            }
        },
        {
            "name": "Mohit Khanna",
            "industry": "technology",
            "expertise": "Data Science & Analytics",
            "experience_years": 8,
            "availability": {
                "monday": ["09:00-11:00"],
                "thursday": ["16:00-18:00"]
            }
        },
        {
            "name": "Aparna Vasudevan",
            "industry": "technology",
            "expertise": "Machine Learning",
            "experience_years": 7,
            "availability": {
                "tuesday": ["14:00-16:00"],
                "saturday": ["10:00-12:00"]
            }
        },
        {
            "name": "Chetan Mahajan",
            "industry": "technology",
            "expertise": "Data Engineering",
            "experience_years": 9,
            "availability": {
                "wednesday": ["15:00-17:00"],
                "friday": ["11:00-13:00"]
            }
        },
        {
            "name": "Benjamin Kaiser",
            "industry": "technology",
            "expertise": "Frontend Development",
            "experience_years": 10,
            "availability": {
                "tuesday": ["09:00-11:00"],
                "friday": ["16:00-18:00"]
            }
        },
        {
            "name": "Anish Chakraborty",
            "industry": "technology",
            "expertise": "Backend Development",
            "experience_years": 12,
            "availability": {
                "wednesday": ["13:00-15:00"],
                "saturday": ["09:00-11:00"]
            }
        },
        {
            "name": "Phong Huynh",
            "industry": "technology",
            "expertise": "Software Architecture",
            "experience_years": 15,
            "availability": {
                "monday": ["11:00-13:00"],
                "thursday": ["15:00-17:00"]
            }
        },
        # Design Mentors
        {
            "name": "Marmik Patel",
            "industry": "design",
            "expertise": "UI/UX Design",
            "experience_years": 7,
            "availability": {
                "monday": ["13:00-15:00"],
                "wednesday": ["16:00-18:00"]
            }
        },
        {
            "name": "Deepa Chauhan",
            "industry": "design",
            "expertise": "Product Design",
            "experience_years": 8,
            "availability": {
                "tuesday": ["11:00-13:00"],
                "friday": ["15:00-17:00"]
            }
        },
        {
            "name": "Nikita Shah",
            "industry": "design",
            "expertise": "UX Research",
            "experience_years": 6,
            "availability": {
                "wednesday": ["14:00-16:00"],
                "saturday": ["11:00-13:00"]
            }
        },
        {
            "name": "Akshay Dalvi",
            "industry": "design",
            "expertise": "Interaction Design",
            "experience_years": 9,
            "availability": {
                "monday": ["16:00-18:00"],
                "thursday": ["13:00-15:00"]
            }
        },
        # Finance Mentors
        {
            "name": "Rajiv Mehta",
            "industry": "finance",
            "expertise": "Investment Banking",
            "experience_years": 14,
            "availability": {
                "tuesday": ["17:00-19:00"],
                "friday": ["10:00-12:00"]
            }
        },
        {
            "name": "Priya Sharma",
            "industry": "finance",
            "expertise": "Financial Analysis",
            "experience_years": 9,
            "availability": {
                "wednesday": ["11:00-13:00"],
                "saturday": ["15:00-17:00"]
            }
        },
        # Healthcare Mentors
        {
            "name": "Dr. Aisha Patel",
            "industry": "healthcare",
            "expertise": "Healthcare Management",
            "experience_years": 12,
            "availability": {
                "monday": ["15:00-17:00"],
                "thursday": ["11:00-13:00"]
            }
        },
        {
            "name": "Dr. Vikram Singh",
            "industry": "healthcare",
            "expertise": "Medical Research",
            "experience_years": 16,
            "availability": {
                "tuesday": ["16:00-18:00"],
                "friday": ["09:00-11:00"]
            }
        },
        # Education Mentors
        {
            "name": "Sunita Krishnan",
            "industry": "education",
            "expertise": "EdTech Innovation",
            "experience_years": 8,
            "availability": {
                "wednesday": ["10:00-12:00"],
                "saturday": ["13:00-15:00"]
            }
        },
        {
            "name": "Arjun Nair",
            "industry": "education",
            "expertise": "Curriculum Development",
            "experience_years": 11,
            "availability": {
                "monday": ["14:00-16:00"],
                "thursday": ["17:00-19:00"]
            }
        }
    ]
    
    mentors_collection.insert_many(mentors)
    print(f"✓ Added {len(mentors)} mentors")
    
    # Seed job opportunities
    print("Seeding job opportunities...")
    jobs = [
        # Data Science Jobs
        {
            "title": "Senior Data Scientist",
            "company": "CodeMaya",
            "description": "Join our team to build advanced machine learning models for predictive analytics and business intelligence solutions.",
            "industry": "technology",
            "location": "Bangalore, India",
            "salary_range": "₹20,00,000 - ₹28,00,000",
            "requirements": "- 5+ years of experience in data science\n- Expertise in Python, R, and SQL\n- Experience with deep learning frameworks\n- Strong statistical knowledge",
            "posted_at": current_date - datetime.timedelta(days=3)
        },
        {
            "title": "Lead ML Engineer, AI Governance",
            "company": "Visa",
            "description": "Lead the development of AI governance frameworks and ensure responsible AI implementation across our products.",
            "industry": "technology",
            "location": "Bangalore, India",
            "salary_range": "₹24,00,000 - ₹35,00,000",
            "requirements": "- 8+ years of experience in ML engineering\n- Experience with AI governance and ethics\n- Strong programming skills in Python\n- Knowledge of regulatory frameworks",
            "posted_at": current_date - datetime.timedelta(days=5)
        },
        # Data Analyst Jobs
        {
            "title": "Data Analyst",
            "company": "Magic Bus India Foundation",
            "description": "Analyze program data to measure impact and provide insights for improving educational initiatives across India.",
            "industry": "nonprofit",
            "location": "Noida, India",
            "salary_range": "₹6,00,000 - ₹9,00,000",
            "requirements": "- Experience in data mining and cleaning\n- Proficiency in data visualization tools\n- Strong analytical skills\n- Knowledge of statistical methods",
            "posted_at": current_date - datetime.timedelta(days=7)
        },
        {
            "title": "Business Intelligence Analyst",
            "company": "Tesco India",
            "description": "Transform complex data into actionable insights to drive business decisions and strategy.",
            "industry": "retail",
            "location": "Bangalore, India",
            "salary_range": "₹12,00,000 - ₹18,00,000",
            "requirements": "- 3+ years of experience in BI\n- Expertise in SQL and Power BI/Tableau\n- Strong problem-solving abilities\n- Experience with retail analytics preferred",
            "posted_at": current_date - datetime.timedelta(days=4)
        },
        # UI/UX Developer Jobs
        {
            "title": "UI/UX Designer",
            "company": "Draupadi's",
            "description": "Design intuitive and visually appealing interfaces for web and mobile applications.",
            "industry": "technology",
            "location": "Kolkata, India",
            "salary_range": "₹8,00,000 - ₹12,00,000",
            "requirements": "- Experience with Figma, Adobe XD or Sketch\n- Knowledge of user research and wireframing\n- Strong portfolio showcasing previous work\n- Understanding of design principles",
            "posted_at": current_date - datetime.timedelta(days=2)
        },
        {
            "title": "Senior UX Designer",
            "company": "Bridge-it",
            "description": "Lead the UX design process for enterprise applications, focusing on user research and interaction design.",
            "industry": "technology",
            "location": "Pune, India",
            "salary_range": "₹15,00,000 - ₹22,00,000",
            "requirements": "- 5+ years of UX design experience\n- Expertise in user research methods\n- Experience with design systems\n- Strong communication and presentation skills",
            "posted_at": current_date - datetime.timedelta(days=8)
        },
        # Frontend Developer Jobs
        {
            "title": "Front-end Developer",
            "company": "IQminds Technology",
            "description": "Develop responsive and interactive user interfaces using modern JavaScript frameworks.",
            "industry": "technology",
            "location": "Noida, India",
            "salary_range": "₹8,00,000 - ₹14,00,000",
            "requirements": "- Proficiency in HTML5, CSS3, and JavaScript\n- Experience with React or Angular\n- Knowledge of responsive design principles\n- Understanding of web accessibility standards",
            "posted_at": current_date - datetime.timedelta(days=4)
        },
        {
            "title": "Senior Frontend Engineer",
            "company": "Leverage Edu",
            "description": "Lead frontend development for our EdTech platform, focusing on performance and user experience.",
            "industry": "education",
            "location": "Gurgaon, India",
            "salary_range": "₹16,00,000 - ₹24,00,000",
            "requirements": "- 5+ years of frontend development experience\n- Expertise in React and state management\n- Experience with frontend testing frameworks\n- Knowledge of performance optimization techniques",
            "posted_at": current_date - datetime.timedelta(days=7)
        },
        # Backend Developer Jobs
        {
            "title": "Backend Developer",
            "company": "Verinite",
            "description": "Build scalable backend services for banking and fintech applications.",
            "industry": "finance",
            "location": "Mumbai, India",
            "salary_range": "₹10,00,000 - ₹18,00,000",
            "requirements": "- Experience in Web API development\n- Knowledge of microservices architecture\n- Proficiency in Java or .NET\n- Understanding of banking domain preferred",
            "posted_at": current_date - datetime.timedelta(days=5)
        },
        # Full Stack Developer Jobs
        {
            "title": "Full Stack Developer (MERN)",
            "company": "Mega Mind Computing Solutions",
            "description": "Develop end-to-end web applications using MongoDB, Express, React, and Node.js.",
            "industry": "technology",
            "location": "Hyderabad, India",
            "salary_range": "₹12,00,000 - ₹18,00,000",
            "requirements": "- Experience with MERN stack\n- Knowledge of RESTful API design\n- Understanding of frontend and backend concepts\n- Experience with version control systems",
            "posted_at": current_date - datetime.timedelta(days=3)
        },
        # Python Developer Jobs
        {
            "title": "Python Developer",
            "company": "DataInsights India",
            "description": "Develop data processing pipelines and analytics tools using Python.",
            "industry": "technology",
            "location": "Chennai, India",
            "salary_range": "₹8,00,000 - ₹14,00,000",
            "requirements": "- Strong Python programming skills\n- Experience with data processing libraries\n- Knowledge of SQL and NoSQL databases\n- Understanding of software design patterns",
            "posted_at": current_date - datetime.timedelta(days=6)
        },
        # Product Management Jobs
        {
            "title": "Product Manager",
            "company": "Flipkart",
            "description": "Lead product strategy and development for our e-commerce platform features.",
            "industry": "technology",
            "location": "Bangalore, India",
            "salary_range": "₹18,00,000 - ₹28,00,000",
            "requirements": "- 3+ years of product management experience\n- Strong analytical and strategic thinking\n- Experience with Agile methodologies\n- Excellent stakeholder management skills",
            "posted_at": current_date - datetime.timedelta(days=9)
        },
        # Finance Jobs
        {
            "title": "Financial Analyst",
            "company": "Global Finance Partners",
            "description": "Perform financial forecasting, reporting, and operational metrics tracking for our clients.",
            "industry": "finance",
            "location": "Mumbai, India",
            "salary_range": "₹10,00,000 - ₹15,00,000",
            "requirements": "- Bachelor's degree in Finance, Accounting, or Economics\n- 2+ years of experience in financial analysis\n- Proficiency in Excel and financial modeling\n- Strong analytical skills",
            "posted_at": current_date - datetime.timedelta(days=7)
        },
        {
            "title": "Investment Analyst",
            "company": "Axis Securities",
            "description": "Analyze investment opportunities and provide recommendations to clients.",
            "industry": "finance",
            "location": "Mumbai, India",
            "salary_range": "₹12,00,000 - ₹18,00,000",
            "requirements": "- MBA in Finance or CFA\n- Strong understanding of Indian equity markets\n- Excellent analytical and research skills\n- Knowledge of financial modeling",
            "posted_at": current_date - datetime.timedelta(days=9)
        },
        # Healthcare Jobs
        {
            "title": "Healthcare Administrator",
            "company": "Apollo Hospitals",
            "description": "Oversee daily operations and ensure high-quality patient care at our healthcare facility.",
            "industry": "healthcare",
            "location": "Delhi, India",
            "salary_range": "₹8,00,000 - ₹12,00,000",
            "requirements": "- Bachelor's degree in Healthcare Administration\n- 3+ years of experience in healthcare management\n- Knowledge of Indian healthcare regulations\n- Strong leadership skills",
            "posted_at": current_date - datetime.timedelta(days=10)
        },
        # Education Jobs
        {
            "title": "EdTech Curriculum Developer",
            "company": "BYJU'S",
            "description": "Develop innovative educational content for K-12 students using digital learning platforms.",
            "industry": "education",
            "location": "Bangalore, India",
            "salary_range": "₹7,00,000 - ₹10,00,000",
            "requirements": "- Master's degree in Education\n- Experience in curriculum development\n- Knowledge of digital learning methodologies\n- Creative approach to educational content",
            "posted_at": current_date - datetime.timedelta(days=2)
        },
        # Marketing Jobs
        {
            "title": "Digital Marketing Specialist",
            "company": "Flipkart",
            "description": "Plan and execute digital marketing campaigns to drive customer acquisition and engagement.",
            "industry": "marketing",
            "location": "Bangalore, India",
            "salary_range": "₹8,00,000 - ₹12,00,000",
            "requirements": "- Experience in digital marketing\n- Knowledge of SEO, SEM, and social media marketing\n- Analytical mindset with data-driven approach\n- Experience with marketing automation tools",
            "posted_at": current_date - datetime.timedelta(days=4)
        },
        {
            "title": "Brand Manager",
            "company": "ITC Limited",
            "description": "Develop and implement brand strategies to enhance brand equity and market position.",
            "industry": "marketing",
            "location": "Kolkata, India",
            "salary_range": "₹14,00,000 - ₹20,00,000",
            "requirements": "- MBA in Marketing\n- 5+ years of brand management experience\n- Strong understanding of consumer behavior\n- Experience in FMCG sector preferred",
            "posted_at": current_date - datetime.timedelta(days=7)
        }
    ]
    
    jobs_collection.insert_many(jobs)
    print(f"✓ Added {len(jobs)} job opportunities")
    
    print("\n" + "="*60)
    print("DATABASE SEEDED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Demo Users: {len(demo_users)}")
    print(f"  • Quiz Responses: {len(demo_quiz_responses)}")
    print(f"  • Mentors: {len(mentors)}")
    print(f"  • Job Opportunities: {len(jobs)}")
    print(f"\n👤 Demo User Credentials:")
    for i, user in enumerate(demo_users):
        print(f"  {i+1}. {user['name']} - {user['email']}")
        print(f"     User ID will be generated - check MongoDB")
    print("\n✅ You can now start the application and test with these demo users!")
    print("="*60)

if __name__ == "__main__":
    seed_database()
