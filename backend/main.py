"""FastAPI Main Entry Point for Emotix Backend."""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from database import Base, engine
from models import * # noqa - ensures all models are registered
import ml_loader

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 EmotiX Backend Starting...")
    # Create DB tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # We might still want to try loading models even if DB fails for diagnostics
    
    # Load ML models
    try:
        ml_loader.load_all_models()
        logger.info("✅ ML models loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ ML models unavailable: {e}")
        logger.warning("⚠️ Starting backend without ML models...")
        
    yield
    logger.info("👋 EmotiX Backend Shutting Down...")

app = FastAPI(
    title="EmotiX Backend",
    description="Your Intelligent Emotion Recognition Platform - REST API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
from routers import auth, behaviour, chat, face, voice, severity, dashboard

app.include_router(auth.router)
app.include_router(behaviour.router)
app.include_router(chat.router)
app.include_router(face.router)
app.include_router(voice.router)
app.include_router(severity.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "EmotiX Backend Running", "version": "1.0.0", "status": "healthy"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models": {
            "behaviour": ml_loader.behaviour_model is not None,
            "face": ml_loader.face_model is not None,
            "voice": ml_loader.voice_cnn_model is not None
        }
    }
