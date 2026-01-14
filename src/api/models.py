from pydantic import BaseModel, Field, ConfigDict
from src.core.models import ClassInfo, Final

class getNearShowsResponse(BaseModel):
    """Response model for getting a list of nearby shows & their dates."""
    shows: list[dict[str, str]]

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

