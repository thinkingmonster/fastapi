from fastapi import FastAPI
from routers import auth, todo

app = FastAPI()

app.include_router(auth.router)
app.include_router(todo.router)
