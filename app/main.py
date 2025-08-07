from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import create_tables, get_db
from .routers import auth, users
from .config import get_settings
from contextlib import asynccontextmanager

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Secure Authentication API",
    description="Enterprise-grade authentication system with JWT and role-based access control",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.environment}

@app.get("/")
def root():
    return {
        "message": "Secure Authentication API",
        "version": "1.0.0",
        "docs": "/docs"
    }
