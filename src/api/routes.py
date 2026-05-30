"""Define API routes."""
import uuid
from fastapi import APIRouter, Query, HTTPException
from src.api.session import session
from src.api.models import *
from src.core.error_logger import log_error, log_info, get_recent_errors, get_error_detail

router = APIRouter(prefix="/api", tags=["Championship Finals API"])

@router.get("/")
def home():
    return {"message": "Welcome to the Championship Finals API"}

@router.get("/near-shows")
async def get_near_shows(response_model=getNearShowsResponse):
    """Fetch the shows that are around the current date."""
    request_id = str(uuid.uuid4())
    log_info(source="GET /api/near-shows", message="Request received", request_id=request_id)
    from .handlers import get_nearby_shows
    try:
        response = await get_nearby_shows()
        shows = response.shows
    except Exception as e:
        log_error(
            error_type="NearShowsError",
            source="GET /api/near-shows",
            cause=str(e),
            request_id=request_id,
            exc=e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    return {"shows": shows}

@router.post("/lookup-ids", response_model=getClassIDsResponse)
async def lookup_ids(request: lookUpIdsRequest):
    """Look up class IDs for a show and height"""
    request_id = str(uuid.uuid4())
    log_info(
        source="POST /api/lookup-ids",
        message=f"Request received — show: {request.show}, height: {request.height}",
        request_id=request_id,
        context={"show": request.show, "height": request.height},
    )
    
    from .handlers import initialise_classInfo
    try:
        response = await initialise_classInfo(request.show, request.height)
        agility_id = response.agilityID
        jumping_id = response.jumpingID
    except Exception as e:
        log_error(
            error_type="LookupIDsError",
            source="POST /api/lookup-ids",
            cause=str(e),
            request_id=request_id,
            context={"show": request.show, "height": request.height},
            exc=e,
        )
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "agilityID": agility_id,
        "jumpingID": jumping_id,
    }

@router.post("/lookup-ids-url", response_model=getClassIDsResponse)
async def lookup_url_ids(request: lookUpUrlIdsRequest):
    """get IDs for backup url input"""
    request_id = str(uuid.uuid4())
    log_info(
        source="POST /api/lookup-ids-url",
        message="Request received",
        request_id=request_id,
        context={"agilityUrl": request.agilityUrl, "jumpingUrl": request.jumpingUrl},
    )

    from .handlers import get_class_ids
    try:
        response = await get_class_ids(request.agilityUrl, request.jumpingUrl)
        agility_id = response.agilityID
        jumping_id = response.jumpingID
    except Exception as e:
        log_error(
            error_type="LookupURLIDsError",
            source="POST /api/lookup-ids-url",
            cause=str(e),
            request_id=request_id,
            context={"agilityUrl": request.agilityUrl, "jumpingUrl": request.jumpingUrl},
            exc=e,
        )
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
    request_id = str(uuid.uuid4())
    log_info(
        source="GET /api/update-classes",
        message="Request received",
        request_id=request_id,
        context={"agilityID": agility, "jumpingID": jumping},
    )
    from .handlers import update_classInfo
    try:
        response = await update_classInfo(str(agility), str(jumping), request_id=request_id)
    except Exception as e:
        log_error(
            error_type="UpdateClassesError",
            source="GET /api/update-classes",
            cause=str(e),
            request_id=request_id,
            context={"agilityID": agility, "jumpingID": jumping},
            exc=e,
        )
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
    request_id = str(uuid.uuid4())
    log_info(
        source="GET /api/final",
        message="Request received",
        request_id=request_id,
        context={"agilityID": agility, "jumpingID": jumping},
    )
    from .handlers import update_classInfo
    try:
        response = await update_classInfo(str(agility), str(jumping), request_id=request_id)
    except Exception as e:
        log_error(
            error_type="FinalDataError",
            source="GET /api/final",
            cause=str(e),
            request_id=request_id,
            context={"agilityID": agility, "jumpingID": jumping},
            exc=e,
        )
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


@router.get("/error-log")
async def error_log(limit: int = Query(default=20, ge=1, le=100, description="Number of recent errors to return")):
    """Return the most recent errors from the error log database."""
    errors = get_recent_errors(limit=limit)
    return {"errors": errors, "count": len(errors)}


@router.get("/error-log/{error_id}")
async def error_log_detail(error_id: int):
    """Return a single error record including its HTML snapshot (if captured)."""
    detail = get_error_detail(error_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Error record {error_id} not found")
    return detail