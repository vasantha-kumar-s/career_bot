# Career Guidance Chatbot Web App

An AI-driven career recommendation system powered by Flask, MongoDB, and Gemini API. This intelligent web application provides personalized career guidance, connects users with mentors, and discovers relevant job opportunities.

## 🌟 Features

- **User Authentication**: Secure login system with separate user and mentor portals
- **Smart Signup**: Create account with integrated career quiz and AI-generated recommendations
- **AI-Powered Chat Interface**: Interactive career guidance using Google's Gemini API
- **Personalized Recommendations**: Get career path suggestions based on your skills and interests
- **Mentor Matching**: Connect with experienced professionals across various industries
- **Job Discovery**: Browse relevant job opportunities tailored to your profile
- **Role-Based Dashboards**: Separate interfaces for users and mentors
- **Responsive Design**: Modern, professional interface

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework) with Flask-Login
- **Database**: MongoDB Atlas (Cloud NoSQL database)
- **AI Engine**: Google Gemini API with fallback support
- **Authentication**: Session-based with secure password hashing
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Icons**: Font Awesome

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB installation)
- Google Gemini API key
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd career_bot
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the root directory:

```env
MONGODB_URI=mongodb+srv://gcorporation04_db_user:oc8e32NtQc6Rjx9Q@cluster0.yzk9icp.mongodb.net/?appName=Cluster0
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note**: The Gemini API key is optional. The application will work in fallback mode without it, providing default career guidance responses.

### 5. Initialize Database

Run the seed script to populate the database with demo data:

```bash
python seed_data.py
```

This will create:
- 3 demo users with sample profiles
- 18+ mentors across various industries
- 20+ job opportunities
- Sample quiz responses and recommendations

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔐 Default Login Credentials

Two default accounts are automatically created on first run:

### User Account
- **Username**: `user`
- **Password**: `password`
- **Type**: Regular user
- **Access**: User dashboard with chat, recommendations, mentors, and jobs

### Mentor Account
- **Username**: `mentor`
- **Password**: `password`
- **Type**: Mentor
- **Access**: Mentor dashboard with mentee management, connection requests

**Important**: Change these credentials in production!

## 🎯 Usage

### For Users
1. **Login**: Use default credentials or create a new account
2. **Signup**: New users complete a 3-step career quiz during signup
   - Step 1: Basic information (name, email, username, password)
   - Step 2: Skills and interests selection
   - Step 3: Education, experience, goals, and location
3. **AI Recommendations**: Get personalized career suggestions generated during signup
4. **Chat Interface**: Discuss career goals with AI-powered assistant
5. **Browse Mentors**: Filter and connect with mentors by industry
6. **Find Jobs**: Discover job opportunities matching your profile

### For Mentors
1. **Login**: Access mentor portal with mentor credentials
2. **View Requests**: See pending connection requests from users
3. **Accept/Reject**: Manage mentee connections
4. **Track Mentees**: View and communicate with active mentees
5. **Profile Management**: Update expertise and availability

## 🏗️ Project Structure

```
career_bot/
├── app.py                      # Main Flask application with authentication
├── app_old.py                  # Original app (backup)
├── db.py                       # MongoDB configuration and default users
├── seed_data.py                # Database seeding script
├── requirements.txt            # Python dependencies
├── templates/
│   ├── login.html             # Login page
│   ├── signup.html            # Signup with career quiz
│   ├── dashboard.html         # User dashboard
│   ├── mentor_dashboard.html  # Mentor dashboard
│   └── index.html             # Original interface (deprecated)
├── PROJECT_NOTES.md           # Technical documentation
├── Procfile                   # Deployment configuration
└── README.md                  # This file
```

## 🔑 Key Features Implementation

### Authentication System

- **Flask-Login Integration**: Session-based authentication with secure password hashing
- **User Roles**: Separate user and mentor account types with role-based access control
- **Signup Quiz**: Multi-step registration form collecting skills, interests, and career goals
- **Auto-Recommendations**: AI generates career suggestions during signup with fallback support

### Backend Logic

- **Explicit Error Handling**: Comprehensive try-except blocks with detailed logging for API failures
- **Gemini API Integration**: Uses Google's Gemini API with explicit failure messages in code
- **Fallback System**: Rule-based recommendations when AI is unavailable or quota exceeded
- **Prompt Structuring**: User context is dynamically built from quiz responses, recommendations, and chat history
- **Response Handling**: Gemini API responses are formatted and displayed with markdown support
- **Data Storage**: All user interactions, quiz responses, and recommendations are stored in MongoDB
- **User-Friendly Messages**: Technical errors are logged but users see friendly, helpful messages

### MongoDB Integration

- **Collections**: Users, Sessions, Quiz Responses, Career Recommendations, Mentors, Mentor Connections, Job Opportunities
- **Indexing**: Optimized indexes for fast queries on frequently accessed fields
- **Aggregation**: Efficient data retrieval using MongoDB queries and filters

### AI Integration

- **Gemini API**: Generates personalized career recommendations and conversational responses
- **Context Awareness**: Maintains conversation history and user profile context
- **Fallback Mechanism**: Provides default responses when API is unavailable

## 🚢 Deployment

### Deployment on Render/Railway/Heroku

1. Set environment variables in your platform's dashboard:
   - `MONGODB_URI`: Your MongoDB connection string
   - `GEMINI_API_KEY`: Your Gemini API key

2. Add a `Procfile` for deployment:
   ```
   web: gunicorn app:app
   ```

3. Deploy using platform-specific commands or Git integration

### Environment Variables Required

- `MONGODB_URI`: MongoDB connection string (required)
- `GEMINI_API_KEY`: Google Gemini API key (optional, will use fallback mode if not provided)
- `SECRET_KEY`: Flask session secret key (auto-generated in development)

## 🔧 Technical Notes

### AI Error Handling

The application includes **explicit error handling** for Gemini API calls:

1. **Code-Level Visibility**: All AI operations use try-except blocks with detailed print statements for debugging
   - Example: `⚠ AI API call failed (expected when quota exceeded)`
   - Logs show exactly when and why API calls fail

2. **User-Friendly Experience**: Despite technical errors in the backend, users always see helpful, friendly messages
   - No technical jargon or error codes shown to users
   - Fallback recommendations are seamlessly provided

3. **Fallback System**: When AI is unavailable, rule-based recommendations ensure the app remains functional
   - Skills-based career matching
   - Default conversation responses
   - Graceful degradation of features

This dual approach allows developers to debug issues while maintaining a professional user experience.

## 📊 API Endpoints

### Authentication
- `GET /` - Redirects to login or dashboard (based on auth status)
- `GET /login` - Login page
- `POST /api/login` - Authenticate user
- `GET /signup` - Signup page with career quiz
- `POST /api/signup` - Create new account with quiz responses
- `GET /logout` - Logout and clear session

### User Dashboard
- `GET /home` - User dashboard (requires login)
- `GET /api/current-user` - Get logged-in user info
- `POST /api/chat` - Send message to AI chatbot
- `GET /api/recommendations` - Get personalized career recommendations
- `GET /api/mentors` - Get list of mentors (filterable by industry/expertise)
- `POST /api/mentor-connection` - Request mentor connection
- `GET /api/jobs` - Get job opportunities (filterable by industry/location)

### Mentor Dashboard
- `GET /mentor-dashboard` - Mentor portal (requires mentor login)
- `GET /api/mentor-stats` - Get mentor statistics
- `GET /api/mentor-requests` - Get pending connection requests
- `GET /api/mentor-mentees` - Get list of active mentees
- `POST /api/mentor-accept` - Accept connection request
- `POST /api/mentor-reject` - Reject connection request

##  License

This project is created for educational and demonstration purposes.
