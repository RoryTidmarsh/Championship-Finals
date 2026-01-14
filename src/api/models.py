from pydantic import BaseModel, Field
from src.core.models import ClassInfo, Final

class getNearShowsResponse(BaseModel):
    """Response model for getting a list of nearby shows & their dates."""
    shows: list[dict[str, str]]


class lookupIDsResponse(BaseModel):
    """Response model for lookup IDs."""
    
    agilityID: str = Field(..., pattern=r"^\d+$", description="Agility round ID")
    jumpingID: str = Field(..., pattern=r"^\d+$", description="Jumping round ID")

class initializeClassInfoResponse(BaseModel):
    """Response model for initializing class info."""
    agilityClass: ClassInfo
    jumpingClass: ClassInfo