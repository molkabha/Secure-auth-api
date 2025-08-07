# Secure Authentication API

Enterprise-grade authentication system built with FastAPI, SQLAlchemy, and JWT, featuring role-based access control, refresh tokens, and secure password hashing.

## Features

- User registration with email, username, and password validation
- Secure password hashing with bcrypt
- JWT access and refresh tokens with expiration and revocation
- Role-based access control (admin and regular users)
- Token refresh endpoint with reuse prevention
- Input validation using Pydantic models
- SQLAlchemy ORM with PostgreSQL backend
- CORS middleware with environment-based settings
- Health check and root endpoints
- Comprehensive automated tests with pytest and pytest-html reporting

## Tech Stack

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0+
- Pydantic v2
- PostgreSQL
- JWT via `python-jose`
- Password hashing via `passlib`
- Testing with pytest and pytest-html

## Setup & Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/secure-auth-api.git
   cd secure-auth-api
Create and activate a virtual environment:

bash
Copier le code
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
Install dependencies:

bash
Copier le code
pip install -r requirements.txt
Configure environment variables:

Create a .env file in the root directory with your settings:

env
Copier le code
DATABASE_URL=postgresql://auth_user:auth_password@localhost:5432/auth_api_db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
Initialize the database (make sure PostgreSQL is running and configured):

The tables will be created automatically on app startup.

Running the Application
Start the FastAPI server:

bash
Copier le code
uvicorn app.main:app --reload
Access API documentation at:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Running Tests
Run tests with detailed HTML report generation:

bash
Copier le code
pytest --html=report.html --self-contained-html
Open report.html in your browser to view the test report.

Project Structure
pgsql
Copier le code

secure-auth-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── crud.py
│   └── routers/
│       ├── auth.py
│       └── users.py
├── tests/
│   ├── test_auth.py
│   └── test_users.py
├── requirements.txt
├── .env
└── README.md

Notes
Update your .env with strong secrets before deploying to production.

Use HTTPS in production for secure token transmission.

Adjust CORS origins in production for security.

Regularly rotate your JWT secret key.

Author
Molka Ben Haj Alaya