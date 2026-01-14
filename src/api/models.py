from pydantic import BaseModel

class getNearShowsResponse(BaseModel):
    """Response model for getting a list of nearby shows & their dates."""
    shows: list[dict[str, str]]


class lookupIDsResponse(BaseModel):
    """Response model for lookup IDs."""
    agilityID: int
    jumpingID: int