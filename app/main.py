from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, profile, accounts

app = FastAPI(title="Personal Finance API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(accounts.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Personal Finance API"}