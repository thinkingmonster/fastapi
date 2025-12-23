# ==================== IMPORTS ====================

# Annotated: Special typing construct that allows adding metadata to type hints
# Used here to attach dependency injection information to type annotations
from dataclasses import field
from os import path
from typing import Annotated, Type

# FastAPI: Main framework class for creating the web application
# Depends: Tells FastAPI to call a function to get a dependency (like database sessions)
from fastapi import FastAPI, Depends, Path

# Session: SQLAlchemy class representing a database connection/transaction
# Used for querying, adding, updating, and deleting records
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

# Import our database configuration module
# Contains: engine (connection manager), SessionLocal (session factory), Base (model base class)
import database

# Import our models module which defines database table structures
# CRITICAL: This import EXECUTES models.py, which registers the Todos class with Base!
# Without this import, Base.metadata wouldn't know about the 'todos' table
import models
from models import Todos

# Import specific items we need frequently
# engine: Database connection engine (connects to todos.db SQLite file)
# SessionLocal: Factory CLASS (not instance) for creating database sessions
from database import engine, SessionLocal


# ==================== APP INITIALIZATION ====================

# Create the FastAPI application instance
# This object handles all HTTP requests, routing, and responses
app = FastAPI()


# ==================== DATABASE SETUP (TESTING) ====================

# TESTING SECTION: Verify that importing models registered the Todos table
# This proves the auto-registration magic of SQLAlchemy's declarative_base()
print("Tables registered with Base:")
print(models.Base.metadata.tables.keys())
# Expected output: dict_keys(['todos'])
# This shows Base "knows" about our Todos table

print("\nTable details:")
# Loop through all registered tables and show their columns
for table_name, table in models.Base.metadata.tables.items():
    print(f"  {table_name}: {table.columns.keys()}")
# Expected output: todos: ['id', 'title', 'description', 'priority', 'complete']


# ==================== CREATE DATABASE TABLES ====================

# Create all tables that Base knows about in the database
# How it works:
#   1. Base.metadata contains all registered table definitions (like Todos)
#   2. create_all() generates CREATE TABLE SQL statements
#   3. Executes them on the database connected to 'engine'
#   4. If todos.db doesn't exist: creates the file
#   5. If 'todos' table doesn't exist: creates it
#   6. If everything exists: does nothing (safe to run multiple times)
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
    # Create a new database session instance
    # SessionLocal is a CLASS (returned by sessionmaker), calling it creates an instance of type Session
    db = SessionLocal()

    # Debugging: Print the type to verify it's a Session instance
    print(type(db))  # <class 'sqlalchemy.orm.session.Session'>

    try:
        # Yield the session to whoever requested it (the endpoint)
        # Execution PAUSES here while endpoint uses the session
        yield db

    finally:
        # This ALWAYS runs after endpoint finishes, even if there was an error
        # Close the session to:
        #   - Commit or rollback any pending transactions
        #   - Release database connection back to the connection pool
        #   - Free up resources
        db.close()


# ==================== TYPE ALIAS FOR DEPENDENCY ====================

# Create a reusable type alias for database dependency
# This makes code cleaner when you have many endpoints that need database access
# Instead of writing: db: Annotated[Session, Depends(get_db)]
# You can write: db: db_dependency
db_dependency = Annotated[Session, Depends(get_db)]
#               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#               Breakdown:
#               - Annotated[...]: Wrapper for adding metadata to types
#               - Session: The actual type (for type checkers)
#               - Depends(get_db): Tells FastAPI "call get_db() to get this value"


# ==================== API ENDPOINTS ====================


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get("/", status_code=HTTP_200_OK)
async def read_all(db: db_dependency):
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
    # Debugging: Print type to verify we received a Session instance
    print(type(db))  # <class 'sqlalchemy.orm.session.Session'>

    # Query all records from the Todos table
    # db.query() creates a Query object
    # models.Todos tells it which table to query
    # .all() executes the query and returns results as a Python list
    # FastAPI automatically serializes Todos objects to JSON
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=f"TODO item {todo_id} not found")


@app.post("/todo", status_code=HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@app.put("/todo/{todo_id}", status_code=HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_id: int, todo_request: TodoRequest):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"TODO item {todo_id} not found")
    todo_model.title = todo_request.title
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority
    todo_model.description = todo_request.description

    db.add(todo_model)
    db.commit()
    

@app.delete("/todo/{todo_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    """
    Delete a todo item by ID.
    
    HTTP Method: DELETE
    URL: /todo/{todo_id}
    
    Parameters:
        db (Session): Database session (dependency injection)
        todo_id (int): ID of the todo to delete (must be > 0)
    
    Returns:
        204 No Content: Success (no body returned)
        404 Not Found: Todo doesn't exist
    
    Database Operations:
        1. Query for todo by ID
        2. If not found, raise 404 error
        3. If found, delete from database
        4. Commit the deletion
    
    Why 204 No Content?
        - 204 means "success, but no response body"
        - DELETE doesn't need to return the deleted item
        - More efficient than 200 with body
    """
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"TODO item {todo_id} not found")
    
    db.delete(todo_model)
    db.commit()


# ==================== NOTES & LEARNING POINTS ====================

"""
KEY CONCEPTS DEMONSTRATED:

1. FACTORY PATTERN:
   - sessionmaker() returns a CLASS (SessionLocal)
   - SessionLocal() creates instances (db sessions)

2. DEPENDENCY INJECTION:
   - Depends(get_db) tells FastAPI to call get_db()
   - Result is injected as function parameter
   - Automatic cleanup via finally block

3. GENERATORS (yield):
   - Function pauses at yield
   - Resumes after caller finishes
   - finally block ALWAYS runs (cleanup guaranteed)

4. TYPE ANNOTATIONS:
   - Annotated[Type, metadata] adds info to types
   - Session is the actual type
   - Depends(...) is metadata for FastAPI

5. ORM (Object-Relational Mapping):
   - Python objects (Todos) map to database tables
   - Query using Python, SQLAlchemy generates SQL
   - Results automatically converted to objects

6. METACLASS MAGIC:
   - Importing models.py registers tables with Base
   - Base uses metaclass to auto-register inherited classes
   - Base.metadata.create_all() creates all registered tables
"""
