from fastapi import FastAPI
from tasks.routes import router as tasks_router

app = FastAPI(title="To-Do List API")

app.include_router(tasks_router)

