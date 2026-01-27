"""Define API routes."""
from fastapi import APIRouter, Query, HTTPException
from src.api.session import session
from src.api.models import *

router = APIRouter(prefix="/api", tags=["Championship Finals API"])

@router.get("/")
def home():
    return {"message": "Welcome to the Championship Finals API"}

@router.get("/near-shows")
async def get_near_shows(response_model=getNearShowsResponse):
    """Fetch the shows that are around the current date."""
    from .handlers import get_nearby_shows
    try:
        response = await get_nearby_shows()
        shows = response.shows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"shows": shows}

@router.post("/lookup-ids", response_model=getClassIDsResponse)
async def lookup_ids(request: lookUpIdsRequest):
    """Look up class IDs for a show and height"""
    print(f"DEBUG: Received request - show: {request.show}, height: {request.height}")
    
    from .handlers import initialise_classInfo
    try:
        response = await initialise_classInfo(request.show, request.height)
        agility_id = response.agilityID
        jumping_id = response.jumpingID
    except Exception as e:
        print(f"DEBUG: Error - {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "agilityID": agility_id,
        "jumpingID": jumping_id,
    }

@router.post("/lookup-ids-url", response_model=getClassIDsResponse)
async def lookup_url_ids(request: lookUpUrlIdsRequest):
    """get IDs for backup url input"""
    print(f"DEBUG: Received request - agilityURL: {request.agilityUrl} | jumpingURL: {request.jumpingUrl}")

    from .handlers import get_class_ids
    try:
        response = await get_class_ids(request.agilityUrl, request.jumpingUrl)
        agility_id = response.agilityID
        jumping_id = response.jumpingID
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "agilityID": agility_id,
        "jumpingID": jumping_id,
    }
        

@router.get("/update-classes")
async def update_classes(
    agility: int = Query(..., description="Agility round ID"), 
    jumping: int = Query(..., description="Jumping round ID")
    ):
    """Update ClassInfo objects with the latest data."""
    from .handlers import update_classInfo
    try:
        response = await update_classInfo(str(agility), str(jumping))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
    
    return {
        "agilityClass": response.agilityClass.to_dict(),
        "jumpingClass": response.jumpingClass.to_dict(),
        "finalClass": response.finalClass.to_dict(),
    }


@router.get("/final")
async def get_final_data(
    agility: int = Query(..., description="Agility round ID"), 
    jumping: int = Query(..., description="Jumping round ID")
    ):
    from .handlers import update_classInfo
    try:
        response = await update_classInfo(str(agility), str(jumping))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get the status of the classes
    agilityStatus = response.agilityClass.status
    jumpingStatus = response.jumpingClass.status

    # Access the winners
    agilityWinner = response.finalClass.agilityWinner
    jumpingWinner = response.finalClass.jumpingWinner

    # Accessing final dataframe
    finalClass = response.finalClass.final_results_df
    finalStatus = response.finalClass.status

    # Convert final dataframe to json object
    final_json = finalClass.to_json()
    print(finalClass.columns.tolist())
    print(final_json)

    # print the types to the console
    print(f"agilityStatus type: {type(agilityStatus)}, jumpingStatus type: {type(jumpingStatus)}")
    print(f"agilityWinner type: {type(agilityWinner)}, jumpingWinner type: {type(jumpingWinner)}")
    print(f"finalClass type: {type(final_json)}")

    return {
        "agilityStatus": agilityStatus,
        "jumpingStatus": jumpingStatus,
        "finalStatus": finalStatus,
        "agilityWinner": agilityWinner,
        "jumpingWinner": jumpingWinner,
        "finalResults": final_json,
    }

@router.get("/requirements")
async def get_requirements(
    agility: int = Query(..., description="Agility round ID"), jumping: int = Query(..., description="Jumping round ID")
    ):
    return {
        "message": "Requirements endpoint is under construction."
    }

@router.get("/health")
async def health_check():
    """Check if API is running"""
    return {"status": "healthy"}