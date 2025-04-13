from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import user, chat, onboarding, diary
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Emogotchi API",
    description="API for the Emogotchi virtual pet application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(onboarding.router, tags=["Onboarding"])
app.include_router(user.router, tags=["User Management"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(diary.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Emogotchi API"} 