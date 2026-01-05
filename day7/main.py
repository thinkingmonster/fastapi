from fastapi import FastAPI
from routers import auth, todo,admin

app = FastAPI()

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
