from datetime import datetime, timedelta
from io import StringIO
import pandas as pd
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
from app.settings.settings import get_settings
from app.schemas.ml_models import MLModel, MLModelCreate
from app.helper.mlModels import get_active_ml_model, create_ml_model
import time
import asyncio

class MlService(object):
    def __init__(self, session):
        self.session = session
        self.settings = get_settings()
        self.reddit_comments_service = RedditCommentsService(session)
        self.reddit_posts_service = RedditPostsService(session)
    
    async def get_active_ml_model(self, prediction_currency: str = None, provider: str = None, model: str = None):
        ml_model = await get_active_ml_model(
            session=self.session,
            prediction_currency=prediction_currency,
            provider=provider,
            model=model
        )
        return ml_model
    
    async def create_ml_model(self, ml_model_create: MLModelCreate):
        ml_model = await create_ml_model(
            session=self.session,
            ml_model_create=ml_model_create
        )
        return ml_model