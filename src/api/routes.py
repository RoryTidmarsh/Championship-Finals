"""Define API routes."""
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/api", tags=["Championship Finals API"])
agilityID = None
jumpingID = None

@router.get("/")
async def root(
    show: str = Query("Wallingford", description="Type of message to display"),
    height: str = Query("XSM",description="Height descriptor"),
):
    return {"message": f"Welcome to the Championship Finals API! You requested {show} show with height {height}.",
    "route": "/"}


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