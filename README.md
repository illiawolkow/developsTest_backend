# Spy Cat Agency (SCA) Management Application

This project is a management application for the Spy Cat Agency (SCA), allowing them to manage spy cats, missions, and targets.

## Backend (FastAPI)

The backend is built using FastAPI and uses an in-memory database for simplicity in this example.

### Features

- **Spy Cats Management:**
    - Create, list, retrieve, update (salary), and delete spy cats.
    - Cat breed validation against [TheCatAPI](https://api.thecatapi.com/v1/breeds).
- **Missions & Targets Management:**
    - Create missions with 1-3 targets.
    - List and retrieve missions.
    - Assign available cats to missions.
    - Update target notes (if target/mission not complete).
    - Mark targets as complete (if all targets complete, mission becomes complete).
    - Delete missions (if not assigned to a cat or if assigned but mission is complete).

### Setup and Running the Backend

1.  **Navigate to the backend directory:**
    ```bash
    cd spy_cat_agency/backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```
    Activate the virtual environment:
    - Windows:
        ```bash
        .venv\Scripts\activate
        ```
    - macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the FastAPI application:**
    The `main.py` file is located inside the `app` subdirectory. To run it with Uvicorn from the `backend` directory:
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will typically be available at `http://127.0.0.1:8000`.
    API documentation (Swagger UI) will be available at `http://127.0.0.1:8000/docs`.
    Alternative API documentation (ReDoc) will be available at `http://127.0.0.1:8000/redoc`.

### API Endpoints (Postman Collection)

[TODO: Add link to Postman collection once created and hosted/exported.]

Key endpoints include:

**Spy Cats (`/cats`)**
*   `POST /cats/`: Create a spy cat.
*   `GET /cats/`: List all spy cats.
*   `GET /cats/{cat_id}`: Get a single spy cat.
*   `PATCH /cats/{cat_id}/salary`: Update a spy cat's salary.
*   `DELETE /cats/{cat_id}`: Delete a spy cat.

**Missions & Targets (`/missions`)**
*   `POST /missions/`: Create a new mission (with targets).
*   `GET /missions/`: List all missions.
*   `GET /missions/{mission_id}`: Get a single mission.
*   `POST /missions/{mission_id}/assign-cat`: Assign a cat to a mission.
*   `PATCH /missions/{mission_id}/targets/{target_id}/notes`: Update target notes.
*   `PATCH /missions/{mission_id}/targets/{target_id}/complete`: Mark a target as complete.
*   `DELETE /missions/{mission_id}`: Delete a mission.


