from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel # For TargetNotesUpdate if it's not in schemas

from .. import crud, schemas, models # Ensure models is imported if used directly

router = APIRouter()

# Schema for updating notes, if not already in schemas.py
class TargetNotesUpdateRequest(BaseModel):
    notes: str

@router.post("/", response_model=schemas.Mission, status_code=status.HTTP_201_CREATED)
async def create_new_mission(mission_in: schemas.MissionCreate):
    """
    Create a new mission along with its targets.
    - A mission must have 1 to 3 targets.
    """
    # Validation for 1-3 targets is handled by Pydantic model `MissionCreate`
    return await crud.create_mission(mission_in=mission_in)

@router.get("/", response_model=List[schemas.Mission])
async def list_all_missions(skip: int = 0, limit: int = 100):
    """List all missions."""
    return await crud.get_missions(skip=skip, limit=limit)

@router.get("/{mission_id}", response_model=schemas.Mission)
async def get_single_mission(mission_id: int):
    """Get a single mission by ID."""
    db_mission = await crud.get_mission(mission_id=mission_id)
    if db_mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    return db_mission

@router.post("/{mission_id}/assign-cat", response_model=schemas.Mission)
async def assign_cat_to_a_mission(mission_id: int, assignment: schemas.MissionAssignment):
    """
    Assign an available cat to a mission.
    - A cat can only be on one mission at a time.
    - A mission can only have one cat assigned.
    """
    # crud.assign_cat_to_mission will handle logic and raise HTTPException for errors
    updated_mission = await crud.assign_cat_to_mission(mission_id=mission_id, cat_id=assignment.cat_id)
    if updated_mission is None: # Should be handled by exceptions in crud typically
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission or Cat not found, or assignment failed")
    return updated_mission

@router.patch("/{mission_id}/targets/{target_id}/notes", response_model=schemas.Target)
async def update_mission_target_notes(
    mission_id: int, 
    target_id: int, 
    notes_update: TargetNotesUpdateRequest # Using the local or schema based model
):
    """
    Update notes for a specific target within a mission.
    - Notes cannot be updated if the target or the mission is complete.
    """
    # crud.update_target_notes will handle logic and raise HTTPException for errors
    updated_target = await crud.update_target_notes(mission_id=mission_id, target_id=target_id, notes=notes_update.notes)
    # Error handling for not found or business logic violations is in crud function
    return updated_target

@router.patch("/{mission_id}/targets/{target_id}/complete", response_model=schemas.Target)
async def mark_mission_target_complete(mission_id: int, target_id: int):
    """
    Mark a specific target as complete.
    - If all targets in a mission are complete, the mission is marked complete.
    - Notes on a completed target are frozen.
    """
    # crud.mark_target_complete will handle logic and raise HTTPException for errors
    updated_target = await crud.mark_target_complete(mission_id=mission_id, target_id=target_id)
    # Error handling is in crud function
    return updated_target

@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_mission(mission_id: int):
    """
    Delete a mission.
    - A mission cannot be deleted if it is assigned to a cat and not yet complete.
    """
    # crud.delete_mission handles the logic and potential HTTPExceptions
    deleted_mission = await crud.delete_mission(mission_id=mission_id)
    if deleted_mission is None:
        # This typically means the mission_id was not found initially.
        # The case where it cannot be deleted due to assignment is handled by HTTPException in crud.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found.")
    return 