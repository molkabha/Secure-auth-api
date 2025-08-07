# Secure Authentication API

![CI](https://github.com/molkabha/secure-auth-api/actions/workflows/tests.yml/badge.svg)

A production-ready authentication system built with FastAPI, PostgreSQL, and JWT. It includes robust security features such as role-based access control, token refresh with reuse prevention, and secure password hashing.

## Features

- User registration with email, username, and password validation
- Password hashing using Bcrypt via `passlib`
- Access and refresh tokens using JWT with expiration and revocation logic
- Role-based access control for admin and regular users
- Token refresh endpoint with token reuse protection
- Input validation using Pydantic models
- Database integration with SQLAlchemy and PostgreSQL
- Environment-based CORS configuration
- Health check and root endpoints
- Automated test suite with Pytest and HTML reporting

## Tech Stack

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0+
- Pydantic v2
- PostgreSQL
- JWT via `python-jose`
- Password hashing via `passlib`
- Pytest with `pytest-html` for test reporting

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/molkabha/secure-auth-api.git
cd secure-auth-api
2. Create and Activate a Virtual Environment
bash
Copier
Modifier
python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copier
Modifier
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory with the following content:

env
Copier
Modifier
DATABASE_URL=postgresql://auth_user:auth_password@localhost:5432/auth_api_db
JWT_SECRET_KEY=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
5. Initialize the Database
Ensure PostgreSQL is running. Tables will be created automatically on application startup.

Running the Application
bash
Copier
Modifier
uvicorn app.main:app --reload
Access the API documentation:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Running Tests
To run the full test suite and generate an HTML report:

bash
Copier
Modifier
pytest --html=report.html --self-contained-html
Open report.html in your browser to view the results.

Project Structure
pgsql
Copier
Modifier
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
Replace secrets in .env before deployment.

Use HTTPS in production to secure token transmission.

Adjust allowed CORS origins appropriately.

Rotate your JWT secret key periodically for enhanced security.

By:
Molka Ben Haj Alaya
