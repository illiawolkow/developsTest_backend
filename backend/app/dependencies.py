import httpx
from fastapi import HTTPException, status, Depends

# Correctly import the schema that will be used in the endpoint
from .schemas import CatCreate # Assuming CatCreate is in schemas.py

THECATAPI_URL = "https://api.thecatapi.com/v1/breeds"

async def validate_cat_breed_from_payload(cat_create_payload: CatCreate) -> CatCreate:
    """
    Validates the cat breed from the CatCreate payload using TheCatAPI.
    This is designed to be used as a FastAPI dependency.
    FastAPI will parse the request body into CatCreate and pass it as cat_create_payload.
    If valid, it returns the original payload; otherwise, raises HTTPException.
    """
    breed_to_validate = cat_create_payload.breed
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(THECATAPI_URL)
            response.raise_for_status()
            breeds_data = response.json()
            if not any(b["name"].lower() == breed_to_validate.lower() for b in breeds_data):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid cat breed: '{breed_to_validate}'. Breed not found in TheCatAPI."
                )
            # If validation passes, return the original payload for the endpoint to use
            return cat_create_payload
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"TheCatAPI service unavailable, could not validate breed: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error from TheCatAPI ({exc.response.status_code}) while validating breed: {exc.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during breed validation: {str(e)}"
            )

# Optional: A simpler function to just get breeds if needed elsewhere
async def get_thecatapi_breeds() -> list:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(THECATAPI_URL)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Simplified error handling for a getter; specific exceptions handled above
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not fetch breeds: {str(e)}") 