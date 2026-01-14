"""Define API routes."""
from fastapi import APIRouter, Query, HTTPException
from src.api.session import session

router = APIRouter(prefix="/api", tags=["Championship Finals API"])

@router.get("/")
def home():
    return {"message": "Welcome to the Championship Finals API"}

@router.get("/near-shows")
async def get_near_shows():
    """Fetch the shows that are around the current date."""
    from .handlers import get_nearby_shows
    try:
        response = await get_nearby_shows()
        shows = response.shows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"shows": shows}

@router.get("/lookup-ids")
async def lookup_ids(
    show: str = Query(..., description="Show name, e.g., 'Championship Finals 2024'"),
    height: str = Query(..., description="Height category, e.g., 'Large'"),
    ):

    from .handlers import initialise_classInfo, get_class_ids
    try:
        agility_class, jumping_class = await initialise_classInfo(show, height)
        agility_id, jumping_id = await get_class_ids(agility_class.results_url, jumping_class.results_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "agilityID": agility_id,
        "jumpingID": jumping_id,
        }

@router.get("/initialise")
async def initialise_classes(
    show: str = Query(..., description="Show name, e.g., 'Championship Finals 2024'"),
    height: str = Query(..., description="Height category, e.g., 'Large'"),
    ):
    """Initialise ClassInfo objects for the given show and height."""
    from .handlers import initialise_classInfo
    try:
        agility_class, jumping_class = await initialise_classInfo(show, height)
        session.initialize_classes(agility_class, jumping_class)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "agilityClass": agility_class,
        "jumpingClass": jumping_class,
        }

@router.get("/update-classes")
async def update_classes(
    agility: int = Query(..., description="Agility round ID"), 
    jumping: int = Query(..., description="Jumping round ID")
    ):
    """Update ClassInfo objects with the latest data."""
    from .handlers import update_classInfo
    try:
        agility_class, jumping_class = await update_classInfo(str(agility), str(jumping))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "agilityClass": agility_class,
        "jumpingClass": jumping_class,
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

@router.get("/status")
async def get_status():
    return {
        "agility": session.agility_class.status if session.agility_class else None,
        "jumping": session.jumping_class.status if session.jumping_class else None,
    }