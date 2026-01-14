"""Define API routes."""
from fastapi import APIRouter, Query, HTTPException
import time

router = APIRouter(prefix="/api", tags=["Championship Finals API"])
agilityID = None
jumpingID = None

date = time.strftime("%Y-%m-%d")

@router.get("/")
def home():
    return {"message": "Welcome to the Championship Finals API"}

@router.get("/lookup-ids")
async def lookup_ids(
    show: str = Query(..., description="Show name, e.g., 'Championship Finals 2024'"),
    height: str = Query(..., description="Height category, e.g., 'Large'"),
    ):

    ## ADD LOGIC TO LOOKUP IDS BASED ON SHOW, DATE AND HEIGHT ##

    agility = 1234  # Placeholder for actual lookup logic
    jumping = 5678  # Placeholder for actual lookup logic
    return {
        "agilityID": agility,
        "jumpingID": jumping,
        }

@router.get("/final")
async def get_final_data(
    agility: int = Query(..., description="Agility round ID"), jumping: int = Query(..., description="Jumping round ID")
    ):
    return {
        "agility": agility,
        "jumping": jumping,
        }

@router.get("/requirements")
async def get_requirements(
    agility: int = Query(..., description="Agility round ID"), jumping: int = Query(..., description="Jumping round ID")
    ):
    return {
        "agility": agility,
        "jumping": jumping,
    }

@router.get("/health")
async def health_check():
    """Check if API is running"""
    return {"status": "healthy"}