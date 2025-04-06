# seed_data.py
from db import SessionLocal, init_db, User, Mentor, JobOpportunity
import json
import datetime

def seed_database():
    """Seed the database with recent data from India for career guidance."""
    # Initialize the database
    init_db()
    
    # Get a database session
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(User).count() > 0:
        print("Database is already seeded.")
        return
    
    # Seed mentors with real data from India across various fields
    mentors = [
        # Technology Mentors
        {
            "name": "Ruchi Chauhan",
            "industry": "technology",
            "expertise": "Data Science",
            "experience_years": 6,
            "availability": json.dumps({
                "monday": ["10:00-12:00", "14:00-16:00"],
                "wednesday": ["10:00-12:00"],
                "friday": ["14:00-16:00"]
            })
        },
        {
            "name": "Syed Quiser Ahmed",
            "industry": "technology",
            "expertise": "Responsible AI",
            "experience_years": 15,
            "availability": json.dumps({
                "tuesday": ["13:00-15:00"],
                "thursday": ["10:00-12:00"]
            })
        },
        {
            "name": "Mohit Khanna",
            "industry": "technology",
            "expertise": "Data Science & Analytics",
            "experience_years": 8,
            "availability": json.dumps({
                "monday": ["09:00-11:00"],
                "thursday": ["16:00-18:00"]
            })
        },
        {
            "name": "Aparna Vasudevan",
            "industry": "technology",
            "expertise": "Machine Learning",
            "experience_years": 7,
            "availability": json.dumps({
                "tuesday": ["14:00-16:00"],
                "saturday": ["10:00-12:00"]
            })
        },
        {
            "name": "Chetan Mahajan",
            "industry": "technology",
            "expertise": "Data Engineering",
            "experience_years": 9,
            "availability": json.dumps({
                "wednesday": ["15:00-17:00"],
                "friday": ["11:00-13:00"]
            })
        },
        {
            "name": "Ekta Shah",
            "industry": "technology",
            "expertise": "Business Intelligence",
            "experience_years": 6,
            "availability": json.dumps({
                "monday": ["17:00-19:00"],
                "thursday": ["09:00-11:00"]
            })
        },
        {
            "name": "Soudamini Sreepada",
            "industry": "technology",
            "expertise": "Statistical Analysis",
            "experience_years": 5,
            "availability": json.dumps({
                "tuesday": ["10:00-12:00"],
                "saturday": ["14:00-16:00"]
            })
        },
        {
            "name": "Marmik Patel",
            "industry": "design",
            "expertise": "UI/UX Design",
            "experience_years": 7,
            "availability": json.dumps({
                "monday": ["13:00-15:00"],
                "wednesday": ["16:00-18:00"]
            })
        },
        {
            "name": "Deepa Chauhan",
            "industry": "design",
            "expertise": "Product Design",
            "experience_years": 8,
            "availability": json.dumps({
                "tuesday": ["11:00-13:00"],
                "friday": ["15:00-17:00"]
            })
        },
        {
            "name": "Nikita Shah",
            "industry": "design",
            "expertise": "UX Research",
            "experience_years": 6,
            "availability": json.dumps({
                "wednesday": ["14:00-16:00"],
                "saturday": ["11:00-13:00"]
            })
        },
        {
            "name": "Akshay Dalvi",
            "industry": "design",
            "expertise": "Interaction Design",
            "experience_years": 9,
            "availability": json.dumps({
                "monday": ["16:00-18:00"],
                "thursday": ["13:00-15:00"]
            })
        },
        {
            "name": "Benjamin Kaiser",
            "industry": "technology",
            "expertise": "Frontend Development",
            "experience_years": 10,
            "availability": json.dumps({
                "tuesday": ["09:00-11:00"],
                "friday": ["16:00-18:00"]
            })
        },
        {
            "name": "Anish Chakraborty",
            "industry": "technology",
            "expertise": "Backend Development",
            "experience_years": 12,
            "availability": json.dumps({
                "wednesday": ["13:00-15:00"],
                "saturday": ["09:00-11:00"]
            })
        },
        {
            "name": "Phong Huynh",
            "industry": "technology",
            "expertise": "Software Architecture",
            "experience_years": 15,
            "availability": json.dumps({
                "monday": ["11:00-13:00"],
                "thursday": ["15:00-17:00"]
            })
        },
        # Finance Mentors
        {
            "name": "Rajiv Mehta",
            "industry": "finance",
            "expertise": "Investment Banking",
            "experience_years": 14,
            "availability": json.dumps({
                "tuesday": ["17:00-19:00"],
                "friday": ["10:00-12:00"]
            })
        },
        {
            "name": "Priya Sharma",
            "industry": "finance",
            "expertise": "Financial Analysis",
            "experience_years": 9,
            "availability": json.dumps({
                "wednesday": ["11:00-13:00"],
                "saturday": ["15:00-17:00"]
            })
        },
        # Healthcare Mentors
        {
            "name": "Dr. Aisha Patel",
            "industry": "healthcare",
            "expertise": "Healthcare Management",
            "experience_years": 12,
            "availability": json.dumps({
                "monday": ["15:00-17:00"],
                "thursday": ["11:00-13:00"]
            })
        },
        {
            "name": "Dr. Vikram Singh",
            "industry": "healthcare",
            "expertise": "Medical Research",
            "experience_years": 16,
            "availability": json.dumps({
                "tuesday": ["16:00-18:00"],
                "friday": ["09:00-11:00"]
            })
        },
        # Education Mentors
        {
            "name": "Sunita Krishnan",
            "industry": "education",
            "expertise": "EdTech Innovation",
            "experience_years": 8,
            "availability": json.dumps({
                "wednesday": ["10:00-12:00"],
                "saturday": ["13:00-15:00"]
            })
        },
        {
            "name": "Arjun Nair",
            "industry": "education",
            "expertise": "Curriculum Development",
            "experience_years": 11,
            "availability": json.dumps({
                "monday": ["14:00-16:00"],
                "thursday": ["17:00-19:00"]
            })
        }
    ]
    
    for mentor_data in mentors:
        mentor = Mentor(**mentor_data)
        db.add(mentor)
    
    # Current date for reference
    current_date = datetime.datetime(2025, 4, 6)
    
    # Seed job opportunities with recent data from India across various roles
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
        
        # Business Analyst Jobs
        {
            "title": "Business Analyst Freshers",
            "company": "ODeX",
            "description": "Analyze business processes and identify opportunities for improvement in our digital logistics platform.",
            "industry": "logistics",
            "location": "Mumbai, India",
            "salary_range": "₹4,50,000 - ₹6,00,000",
            "requirements": "- Bachelor's degree in Business/Economics/Engineering\n- Strong analytical thinking\n- Excellent communication skills\n- Knowledge of business process modeling",
            "posted_at": current_date - datetime.timedelta(days=2)
        },
        {
            "title": "Associate Business Analyst",
            "company": "TSS Consultancy Pvt. Ltd.",
            "description": "Work with stakeholders to gather requirements and translate them into effective business solutions.",
            "industry": "consulting",
            "location": "Mumbai, India",
            "salary_range": "₹5,00,000 - ₹7,00,000",
            "requirements": "- 0-2 years of experience\n- Strong documentation skills\n- Ability to identify business problems\n- Knowledge of business analysis techniques",
            "posted_at": current_date - datetime.timedelta(days=6)
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
            "title": "AEM Backend Developer",
            "company": "Appson Technologies",
            "description": "Develop and maintain backend services for HDFC projects using Adobe Experience Manager.",
            "industry": "technology",
            "location": "Remote",
            "salary_range": "₹15,00,000 - ₹20,00,000",
            "requirements": "- 6+ years of AEM backend development experience\n- Strong Java programming skills\n- Experience with OSGi/FELIX\n- Knowledge of JCR/CRX and Apache Sling",
            "posted_at": current_date - datetime.timedelta(days=12)
        },
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
        {
            "title": "Senior Full Stack Engineer",
            "company": "Top Mentor",
            "description": "Lead development of our educational platform, handling both frontend and backend responsibilities.",
            "industry": "education",
            "location": "Pune, India",
            "salary_range": "₹18,00,000 - ₹25,00,000",
            "requirements": "- 5+ years of full stack development experience\n- Proficiency in React and Node.js\n- Experience with database design and optimization\n- Knowledge of cloud services (AWS/Azure)",
            "posted_at": current_date - datetime.timedelta(days=9)
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
        {
            "title": "Senior Python Engineer",
            "company": "AI Innovations India",
            "description": "Develop and optimize machine learning models and AI applications using Python.",
            "industry": "technology",
            "location": "Bangalore, India",
            "salary_range": "₹16,00,000 - ₹25,00,000",
            "requirements": "- 5+ years of Python development experience\n- Expertise in ML frameworks (TensorFlow/PyTorch)\n- Experience with cloud deployment\n- Knowledge of software architecture",
            "posted_at": current_date - datetime.timedelta(days=8)
        },
        
        # Java Developer Jobs
        {
            "title": "Java Developer",
            "company": "Technopinch Solutions",
            "description": "Develop enterprise applications using Java and related technologies.",
            "industry": "technology",
            "location": "Pune, India",
            "salary_range": "₹8,00,000 - ₹15,00,000",
            "requirements": "- Strong Java programming skills\n- Experience with Spring Boot\n- Knowledge of relational databases\n- Understanding of RESTful services",
            "posted_at": current_date - datetime.timedelta(days=7)
        },
        {
            "title": "Senior Java Engineer",
            "company": "Global PayEX",
            "description": "Lead development of financial services applications using Java technologies.",
            "industry": "finance",
            "location": "Mumbai, India",
            "salary_range": "₹18,00,000 - ₹28,00,000",
            "requirements": "- 8+ years of Java development experience\n- Expertise in Spring Framework\n- Experience with microservices architecture\n- Knowledge of financial domain preferred",
            "posted_at": current_date - datetime.timedelta(days=10)
        },
        
        # Cloud Developer Jobs
        {
            "title": "Cloud Developer",
            "company": "CloudTech Solutions",
            "description": "Design and implement cloud-based solutions using AWS and Azure.",
            "industry": "technology",
            "location": "Remote",
            "salary_range": "₹12,00,000 - ₹20,00,000",
            "requirements": "- Experience with AWS/Azure services\n- Knowledge of cloud architecture patterns\n- Strong programming skills in Python/Java\n- Understanding of DevOps practices",
            "posted_at": current_date - datetime.timedelta(days=5)
        },
        {
            "title": "Senior Cloud Engineer",
            "company": "TechWave Solutions",
            "description": "Lead cloud migration projects and optimize cloud infrastructure for performance and cost.",
            "industry": "technology",
            "location": "Bangalore, India",
            "salary_range": "₹20,00,000 - ₹30,00,000",
            "requirements": "- 5+ years of cloud engineering experience\n- Expertise in AWS/Azure architecture\n- Experience with Kubernetes and Docker\n- Strong problem-solving skills",
            "posted_at": current_date - datetime.timedelta(days=9)
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
        {
            "title": "Medical Research Analyst",
            "company": "Biocon",
            "description": "Analyze clinical trial data and prepare reports for regulatory submissions.",
            "industry": "healthcare",
            "location": "Bangalore, India",
            "salary_range": "₹9,00,000 - ₹14,00,000",
            "requirements": "- Master's degree in Life Sciences or Pharmacy\n- Experience with clinical data analysis\n- Knowledge of regulatory requirements\n- Strong attention to detail",
            "posted_at": current_date - datetime.timedelta(days=6)
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
        {
            "title": "Education Consultant",
            "company": "Vedantu",
            "description": "Provide guidance to students and parents on educational pathways and career options.",
            "industry": "education",
            "location": "Hyderabad, India",
            "salary_range": "₹6,00,000 - ₹9,00,000",
            "requirements": "- Bachelor's degree in Education or related field\n- Experience in student counseling\n- Knowledge of Indian education system\n- Excellent communication skills",
            "posted_at": current_date - datetime.timedelta(days=8)
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
    
    for job_data in jobs:
        job = JobOpportunity(**job_data)
        db.add(job)
    
    # Commit changes
    db.commit()
    db.close()
    
    print("Database seeded successfully with recent data from India!")

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully with recent data from India!")