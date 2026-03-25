from pydantic import BaseModel, Field
from typing import List, Optional

# --- Requests ---

class RecommendationRequest(BaseModel):
    company: Optional[str] = None
    customer: Optional[str] = None
    route: str
    lot_id: str = ""
    is_low_pip: bool = False
    require_solid_carbon: bool = False

class AllocationRequest(BaseModel):
    grid_id: str
    route: str
    borrower: str
    grid_type: Optional[str] = None

# --- Responses ---

class GridOptionResponse(BaseModel):
    companies: List[str]
    customer_map: dict
    routes: List[str]

class RecommendationItem(BaseModel):
    grid_id: str = Field(..., alias="Grid ID")
    grid_type: str = Field(..., alias="Grid Type")
    slots: str = Field(..., alias="Slots")
    score: int = Field(..., alias="Score")
    reasons: str = Field(..., alias="Reasons")
    raw_status: str = Field(..., alias="Raw_Status")

    class Config:
        populate_by_name = True

class RecommendationResponse(BaseModel):
    candidates: List[RecommendationItem]

class BaseResponse(BaseModel):
    status: str
    message: str

class InventoryItem(BaseModel):
    grid_id: str
    grid_type: str
    current_samples_count: int
    assigned_lot_id: Optional[str] = None
    is_low_pip: bool
    exclusive_lot_id: Optional[str] = None
    status: str

class InventoryResponse(BaseModel):
    items: List[InventoryItem]