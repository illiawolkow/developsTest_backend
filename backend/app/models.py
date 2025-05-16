from pydantic import BaseModel, Field
from typing import List, Optional

class TargetBase(BaseModel):
    name: str
    country: str
    notes: Optional[str] = None
    is_complete: bool = False

class TargetCreate(TargetBase):
    pass

class Target(TargetBase):
    id: int

    class Config:
        from_attributes = True # Replaces orm_mode = True in Pydantic v2

class MissionBase(BaseModel):
    is_complete: bool = False

class MissionCreate(MissionBase):
    targets: List[TargetCreate] = Field(..., min_length=1, max_length=3)

class Mission(MissionBase):
    id: int
    cat_id: Optional[int] = None
    targets: List[Target] = []

    class Config:
        from_attributes = True

class CatBase(BaseModel):
    name: str
    years_of_experience: int = Field(..., ge=0)
    breed: str
    salary: float = Field(..., gt=0)

class CatCreate(CatBase):
    pass

class CatUpdate(BaseModel):
    salary: Optional[float] = Field(None, gt=0)

class Cat(CatBase):
    id: int
    mission_id: Optional[int] = None

    class Config:
        from_attributes = True

class MissionAssignment(BaseModel):
    cat_id: int 