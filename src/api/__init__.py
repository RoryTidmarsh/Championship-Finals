from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
app = FastAPI(
    title="Champ Finals API",
    version="1.0.0",
    description="API accessing real-time data for the Championship Finals.",
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

from . import routes  # Import routes to register them with the FastAPI app
app.include_router(routes.router)