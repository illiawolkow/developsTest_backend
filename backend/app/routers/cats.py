from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel

from .. import crud, schemas, models
from ..dependencies import validate_cat_breed_from_payload

router = APIRouter()

class TargetNotesUpdate(BaseModel):
    notes: str

@router.post("/", response_model=schemas.Cat, status_code=status.HTTP_201_CREATED)
async def create_spy_cat(
    cat_in: schemas.CatCreate = Depends(validate_cat_breed_from_payload)
):
    """
    Create a new spy cat.
    - **name**: Each cat must have a name.
    - **years_of_experience**: Must be a non-negative integer.
    - **breed**: Must be a valid breed according to TheCatAPI.
    - **salary**: Must be a positive number.
    """
    return await crud.create_cat(cat_in=cat_in)

@router.get("/", response_model=List[schemas.Cat])
async def list_spy_cats(skip: int = 0, limit: int = 100):
    """List all spy cats."""
    return await crud.get_cats(skip=skip, limit=limit)

@router.get("/{cat_id}", response_model=schemas.Cat)
async def get_spy_cat(cat_id: int):
    """Get a single spy cat by ID."""
    db_cat = await crud.get_cat(cat_id=cat_id)
    if db_cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spy cat not found")
    return db_cat

@router.patch("/{cat_id}/salary", response_model=schemas.Cat)
async def update_spy_cat_salary(
    cat_id: int, 
    salary_update: schemas.CatUpdate
):
    """Update a spy cat's salary."""
    if salary_update.salary is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Salary must be provided for update.")
    
    updated_cat = await crud.update_cat_salary(cat_id=cat_id, salary=salary_update.salary)
    if updated_cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spy cat not found")
    return updated_cat

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spy_cat(cat_id: int):
    """Delete a spy cat."""
    deleted_cat = await crud.delete_cat(cat_id=cat_id)
    if deleted_cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spy cat not found.")
    return 