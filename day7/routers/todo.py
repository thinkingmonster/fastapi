from dataclasses import field
from typing import Annotated, Type
from fastapi import APIRouter, Depends, Path


from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

import database

import models
from models import Todos
from database import engine, SessionLocal
from routers.auth import get_current_user


router = APIRouter(prefix="/todo", tags=["todo"])


models.Base.metadata.create_all(bind=database.engine)


# ==================== DEPENDENCY INJECTION FUNCTIONS ====================


def get_db():
    """
    Database session dependency generator.

    This is a GENERATOR function (uses 'yield' instead of 'return').
    FastAPI calls this function via Depends(get_db) to provide database sessions to endpoints.

    Flow:
        1. Create new session
        2. Yield (pause) and give session to endpoint
        3. Endpoint uses session
        4. Endpoint returns
        5. Resume here and run 'finally' block
        6. Close session (cleanup)

    Why use 'yield' instead of 'return'?
        - 'return' can't guarantee cleanup if endpoint crashes
        - 'yield' with 'finally' ALWAYS runs cleanup code
        - This pattern is called a "generator context manager"

    Yields:
        Session: A database session for querying/modifying the database
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    """
    Get all todos from the database.

    HTTP Method: GET
    URL: /

    Parameters:
        db (Session): Database session automatically injected by FastAPI

    How dependency injection works here:
        1. User makes request: GET /
        2. FastAPI sees 'db: db_dependency' parameter
        3. FastAPI expands db_dependency: Annotated[Session, Depends(get_db)]
        4. FastAPI sees Depends(get_db) - "Need to call get_db()!"
        5. FastAPI calls get_db() which yields a Session instance
        6. FastAPI passes that Session as 'db' parameter
        7. This function executes with db = Session instance
        8. Function returns list of todos
        9. FastAPI converts todos to JSON
        10. FastAPI ensures get_db's finally block runs (closes session)
        11. Response sent to user

    Returns:
        List[Todos]: All todo items from database as JSON
        Example: [
            {
                "id": 1,
                "title": "Buy groceries",
                "description": "Get milk, eggs, bread",
                "priority": 3,
                "complete": false
            },
            ...
        ]

    Database Query Breakdown:
        db.query(models.Todos)  - Create a query object for Todos table
        .all()                  - Execute query and return ALL results as list
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}", status_code=HTTP_200_OK)
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f"TODO item {todo_id} not found")


@router.post("/", status_code=HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code=HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"TODO item {todo_id} not found")
    todo_model.title = todo_request.title
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority
    todo_model.description = todo_request.description

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"TODO item {todo_id} not found")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()
    
