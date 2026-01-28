from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI app lifespan - startup and shutdown.
    """
    # Startup
    yield
    # Shutdown - no cleanup needed for now

app = FastAPI(
    title="Champ Finals API",
    version="1.0.0",
    description="API accessing real-time data for the Championship Finals.",
    lifespan=lifespan,
)

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
# Strip whitespace from each origin
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

from . import routes  # Import routes to register them with the FastAPI app
app.include_router(routes.router)