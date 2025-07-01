import logging
import sys
from contextlib import asynccontextmanager

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

import uvicorn
# from app.api.routers.users import router as users_router
from app.settings.settings import settings
from app.database import sessionmanager
from fastapi import FastAPI

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.debug_logs else logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()

app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")

@app.get("/")
async def root():
    return {"message": "Hello World"}