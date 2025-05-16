from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORS middleware
from contextlib import asynccontextmanager

from .routers import cats, missions
from . import crud # For reset_db_state, if used

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(current_app: FastAPI):
    # Startup: Initialize or reset database state (useful for in-memory dbs during dev)
    await crud.reset_db_state() # Resetting on each startup for fresh state
    print("Spy Cat Agency API starting up...")
    print("In-memory database has been reset.")
    yield
    # Shutdown
    print("Spy Cat Agency API shutting down...")

app = FastAPI(
    title="Spy Cat Agency API",
    description="Manage spy cats, their missions, and targets.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware Configuration
# Define the origins that are allowed to make cross-origin requests.
# For development, this often includes your frontend's development server URL.
origins = [
    "http://localhost:3000", # Next.js default development port
    "http://localhost:3001", # Another common frontend dev port
    # Add other origins if needed, e.g., your deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["*"],    # Allow all standard methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers
)

print(f"DEBUG: cats module is {cats}")
print(f"DEBUG: cats.router is {getattr(cats, 'router', 'not found')}")
app.include_router(cats.router, prefix="/cats", tags=["Spy Cats"])
print("DEBUG: Cats router included.")

print(f"DEBUG: missions module is {missions}")
print(f"DEBUG: missions.router is {getattr(missions, 'router', 'not found')}")
app.include_router(missions.router, prefix="/missions", tags=["Missions & Targets"])
print("DEBUG: Missions router included.")

@app.get("/", tags=["Root"], summary="Root path for the API")
async def read_root():
    return {"message": "Welcome to the Spy Cat Agency API!"}

# To run this app (save as main.py in the app folder, then from parent of app folder):
# uvicorn backend.app.main:app --reload 