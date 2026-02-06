# Request model
from pydantic import BaseModel, Field
from typing import List


class UpdateEquipmentsRequest(BaseModel):
    unavailableEquipmentIds: List[int]

class UpdateExperienceRequest(BaseModel):
    experienceLevel: int = Field(..., ge=1, le=3)


class UpdateGoalRequest(BaseModel):
    id: int = Field(..., ge=1, le=10)