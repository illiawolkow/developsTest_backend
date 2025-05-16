from typing import List, Dict, Optional, Union
from fastapi import HTTPException, status

from . import models, schemas

# In-memory storage
fake_cats_db: Dict[int, models.Cat] = {}
fake_missions_db: Dict[int, models.Mission] = {}
fake_targets_db: Dict[int, models.Target] = {}

next_cat_id = 1
next_mission_id = 1
next_target_id = 1

# Helper to reset DB for testing or re-runs if needed (not for production)
async def reset_db_state():
    global fake_cats_db, fake_missions_db, fake_targets_db
    global next_cat_id, next_mission_id, next_target_id
    fake_cats_db = {}
    fake_missions_db = {}
    fake_targets_db = {}
    next_cat_id = 1
    next_mission_id = 1
    next_target_id = 1

# --- Spy Cats CRUD ---
async def create_cat(cat_in: schemas.CatCreate) -> models.Cat:
    global next_cat_id
    if any(existing_cat.name == cat_in.name and existing_cat.breed == cat_in.breed for existing_cat in fake_cats_db.values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A cat with the same name and breed already exists.")
    
    db_cat = models.Cat(
        id=next_cat_id,
        name=cat_in.name,
        years_of_experience=cat_in.years_of_experience,
        breed=cat_in.breed,
        salary=cat_in.salary,
        mission_id=None
    )
    fake_cats_db[next_cat_id] = db_cat
    next_cat_id += 1
    return db_cat

async def get_cat(cat_id: int) -> Optional[models.Cat]:
    return fake_cats_db.get(cat_id)

async def get_cats(skip: int = 0, limit: int = 100) -> List[models.Cat]:
    return list(fake_cats_db.values())[skip : skip + limit]

async def update_cat_salary(cat_id: int, salary: float) -> Optional[models.Cat]:
    if cat_id not in fake_cats_db:
        return None
    fake_cats_db[cat_id].salary = salary
    return fake_cats_db[cat_id]

async def delete_cat(cat_id: int) -> Optional[models.Cat]:
    # Check if cat is on a mission
    if cat_id in fake_cats_db and fake_cats_db[cat_id].mission_id is not None:
        mission = await get_mission(fake_cats_db[cat_id].mission_id)
        if mission and not mission.is_complete:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete cat assigned to an active mission.")

    return fake_cats_db.pop(cat_id, None)

# --- Missions / Targets CRUD ---

async def create_mission(mission_in: schemas.MissionCreate) -> models.Mission:
    global next_mission_id, next_target_id
    
    db_targets = []
    for target_in in mission_in.targets:
        db_target = models.Target(
            id=next_target_id,
            name=target_in.name,
            country=target_in.country,
            notes=target_in.notes,
            is_complete=False
        )
        fake_targets_db[next_target_id] = db_target
        db_targets.append(db_target)
        next_target_id += 1

    db_mission = models.Mission(
        id=next_mission_id,
        targets=db_targets,
        is_complete=False,
        cat_id=None # Initially unassigned
    )
    fake_missions_db[next_mission_id] = db_mission
    next_mission_id += 1
    return db_mission

async def get_mission(mission_id: int) -> Optional[models.Mission]:
    mission = fake_missions_db.get(mission_id)
    if not mission: 
        return None
    # Ensure targets are correctly populated from fake_targets_db if they were just IDs
    # In our current model structure, Mission directly holds Target objects, 
    # so this step might be redundant if create_mission populates it fully.
    # However, if Mission only stored target_ids, this would be crucial.
    # For consistency with how we might fetch from a real DB:
    fetched_targets = []
    for target_model in mission.targets: # mission.targets should hold full Target models
        if target_model.id in fake_targets_db:
            fetched_targets.append(fake_targets_db[target_model.id])
    mission.targets = fetched_targets
    return mission

async def get_missions(skip: int = 0, limit: int = 100) -> List[models.Mission]:
    missions = list(fake_missions_db.values())[skip : skip + limit]
    # Similar to get_mission, ensure targets are fresh
    for mission in missions:
        fetched_targets = []
        for target_model in mission.targets:
            if target_model.id in fake_targets_db:
                fetched_targets.append(fake_targets_db[target_model.id])
        mission.targets = fetched_targets
    return missions

async def assign_cat_to_mission(mission_id: int, cat_id: int) -> Optional[models.Mission]:
    mission = await get_mission(mission_id)
    cat = await get_cat(cat_id)

    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found")
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cat with id {cat_id} not found")

    if mission.cat_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Mission {mission_id} is already assigned to cat {mission.cat_id}")
    if cat.mission_id is not None:
        # Check if the assigned mission is actually active
        assigned_mission = await get_mission(cat.mission_id)
        if assigned_mission and not assigned_mission.is_complete:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cat {cat_id} is already on an active mission {cat.mission_id}")

    mission.cat_id = cat_id
    cat.mission_id = mission_id
    return mission

async def update_target_notes(mission_id: int, target_id: int, notes: str) -> Optional[models.Target]:
    mission = await get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission {mission_id} not found.")
    if mission.is_complete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update notes on a completed mission.")

    target = fake_targets_db.get(target_id)
    if not target or target not in mission.targets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Target {target_id} not found in mission {mission_id}.")
    if target.is_complete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update notes on a completed target.")

    target.notes = notes
    return target

async def mark_target_complete(mission_id: int, target_id: int) -> Optional[models.Target]:
    mission = await get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission {mission_id} not found.")
    # Cannot mark target complete if mission is already complete (though this state should be derived)
    if mission.is_complete:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mission is already complete. Cannot modify targets.")

    target = fake_targets_db.get(target_id)
    if not target or target not in mission.targets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Target {target_id} not found in mission {mission_id}.")
    
    if target.is_complete:
        # Idempotency: if already complete, just return the target
        return target

    target.is_complete = True
    
    # Check if all targets in the mission are complete
    all_targets_complete = all(t.is_complete for t in mission.targets)
    if all_targets_complete:
        mission.is_complete = True
        # If mission is complete, the cat is now free
        if mission.cat_id and mission.cat_id in fake_cats_db:
            fake_cats_db[mission.cat_id].mission_id = None
            
    return target

async def delete_mission(mission_id: int) -> Optional[models.Mission]:
    mission = await get_mission(mission_id)
    if not mission:
        return None # Or raise 404 if preferred for delete operations

    if mission.cat_id is not None:
        # Check if the cat is still assigned *and* mission is not complete
        # If mission is complete, cat should have been unassigned.
        cat = await get_cat(mission.cat_id)
        if cat and cat.mission_id == mission_id and not mission.is_complete:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a mission that is currently assigned to a cat and is not complete.")

    # Delete associated targets first to maintain consistency
    for target in list(mission.targets): # Iterate over a copy
        fake_targets_db.pop(target.id, None)
    
    # Then delete the mission
    return fake_missions_db.pop(mission_id, None) 