# db.py - Database Models
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import datetime

DATABASE_URL = "sqlite:///career_guidance.db"
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True, pool_size=10, max_overflow=20)
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    demographics = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    quiz_responses = relationship("QuizResponse", back_populates="user")
    recommendations = relationship("CareerRecommendation", back_populates="user")
    mentor_connections = relationship("MentorConnection", back_populates="user")

class UserSession(Base):
    __tablename__ = "user_sessions"
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    conversation_history = Column(Text)  # JSON array of messages
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class QuizResponse(Base):
    __tablename__ = "quiz_responses"
    response_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    question = Column(Text)
    answer = Column(Text)
    quiz_type = Column(String, index=True)  # "experience", "skills", "interests", etc.
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="quiz_responses")
    
    # Add compound index for faster filtering by user_id and quiz_type
    __table_args__ = (Index('idx_user_quiz_type', "user_id", "quiz_type"),)

class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"
    recommendation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    career_path = Column(String, index=True)
    recommendation_text = Column(Text)
    confidence_score = Column(Integer)  # 0-100 score of recommendation confidence
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")

class Mentor(Base):
    __tablename__ = "mentors"
    mentor_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, index=True)
    expertise = Column(String, index=True)
    experience_years = Column(Integer)
    availability = Column(String)  # JSON string for availability schedule
    
    # Relationships
    connections = relationship("MentorConnection", back_populates="mentor")
    
    # Add compound index for faster filtering by industry and expertise
    __table_args__ = (Index('idx_industry_expertise', "industry", "expertise"),)

class MentorConnection(Base):
    __tablename__ = "mentor_connections"
    connection_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.mentor_id"), index=True)
    status = Column(String, index=True)  # pending, connected, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="mentor_connections")
    mentor = relationship("Mentor", back_populates="connections")
    
    # Add compound index for faster lookups
    __table_args__ = (Index('idx_user_mentor', "user_id", "mentor_id"),)

class JobOpportunity(Base):
    __tablename__ = "job_opportunities"
    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, index=True)
    description = Column(Text)
    industry = Column(String, index=True)
    location = Column(String, index=True)
    salary_range = Column(String)
    requirements = Column(Text)
    posted_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Add compound index for common filters
    __table_args__ = (Index('idx_industry_location', "industry", "location"),)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()