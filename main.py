from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import onboarding, chat, user

app = FastAPI(
    title="Emogotchi API",
    description="Backend API for Emogotchi application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboarding.router, tags=["onboarding"])
app.include_router(chat.router, tags=["chat"])
app.include_router(user.router, tags=["user"])

@app.get("/")
async def root():
    return {"message": "Welcome to Emogotchi API"} 