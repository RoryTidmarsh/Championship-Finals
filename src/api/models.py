from pydantic import BaseModel, Field, ConfigDict
from src.core.models import ClassInfo, Final

class getNearShowsResponse(BaseModel):
    """Response model for getting a list of nearby shows & their dates."""
    shows: list[dict[str, str]]

class lookUpIdsRequest(BaseModel):
    """Request model for looking up IDs"""
    show: str
    height: str

class lookupIDsResponse(BaseModel):
    """Response model for looking up class IDs."""
    agilityID: str = Field(..., pattern=r"^\d+$", description="Agility class ID")
    jumpingID: str = Field(..., pattern=r"^\d+$", description="Jumping class ID")

class getStatusResponse(BaseModel):
    """Response model for getting status of classes."""
    agilityStatus: str | None
    jumpingStatus: str | None

class update_classesResponse(BaseModel):
    """Response model for updating class info."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    agilityClass: ClassInfo
    jumpingClass: ClassInfo
    finalClass: Final

# class initialiseClassInfoResponse(BaseModel):
#     """Response model for initializing class info."""
#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     agilityClass: ClassInfo
#     jumpingClass: ClassInfo

# class getClassIDsResponse(BaseModel):
#     """Response model for getting class IDs."""
#     agilityID: str = Field(..., pattern=r"^\d+$", description="Agility class ID")
#     jumpingID: str = Field(..., pattern=r"^\d+$", description="Jumping class ID")

# class updateClassInfoResponse(BaseModel):
#     """Response model for updating class info."""
#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     agilityClass: ClassInfo
#     jumpingClass: ClassInfo

