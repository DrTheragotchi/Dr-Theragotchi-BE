from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import user, chat

app = FastAPI(
    title="Emogotchi API",
    description="Backend API for Emogotchi application",
    version="1.0.0"
)

# Configure CORS for Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins temporarily
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Explicitly list all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"],  # Exposes all headers to the client
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers
app.include_router(user.router, tags=["user"])
app.include_router(chat.router, tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to Emogotchi API"}

# Global exception handler to ensure clean JSON responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    ) 