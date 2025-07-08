import logging
import sys
from contextlib import asynccontextmanager

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from app.api.routers.redditPosts import router as redditPosts_router
from app.api.routers.redditComments import router as redditComments_router
from app.settings.settings import get_settings
from app.database import sessionmanager
from fastapi import FastAPI

settings = get_settings()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.debug_logs else logging.INFO)

# --- disable SQLAlchemy logs before ANY imports ---
for logger_name in list(logging.root.manager.loggerDict.keys()):
    if logger_name.startswith("sqlalchemy"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = False
        logger.setLevel(logging.CRITICAL)

# Override noisy libraries
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

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

# Routers
app.include_router(redditPosts_router)
app.include_router(redditComments_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=settings.app_port, log_level=settings.log_level.lower())