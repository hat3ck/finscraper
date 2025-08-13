from datetime import datetime, timedelta
from io import StringIO
import pandas as pd
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
from app.services.llmService import LLMService
from app.services.currencyPricesService import CurrencyPricesService
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
        self.reddit_llm_service = LLMService(session)
        self.currency_prices_service = CurrencyPricesService(session)
    
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

    async def predict_currencies_sentiment(self, prediction_hour_interval: int = 12):
        # Get a list of currencies to predict
        currencies = self.settings.currency_list
        # get reddit posts, comments, and sentiments from the beginning of 2025 till now
        start_date = int(datetime(2025, 1, 1).timestamp())
        end_date = int(datetime.now().timestamp())
        # TODO: IMPLEMENT THE REST
        # add currency prices to the DataFrame
        # for each currency call the prediction function
        predictions = []

    async def prepare_sentiment_data(self, start_date: int, end_date: int, prediction_hour_interval: int = 12):
        extracted_sentiments = await self.reddit_llm_service.get_reddit_posts_comments_sentiments_by_date_range(
            start_date_timestamp=start_date,
            end_date_timestamp=end_date
        )
        merged_df = await self.add_currency_prices_to_sentiment_data(
            extracted_sentiments=extracted_sentiments,
            start_date=start_date,
            end_date=end_date,
            prediction_hour_interval=prediction_hour_interval
        )
        # 6. create a field called hours_since_ath
        row_timestamp = merged_df['created_utc_y'].astype(int) / 10**9
        # convert ath_now to timestamp and get the difference in hours with only 2 decimals
        merged_df['hours_since_ath'] = round((row_timestamp - pd.to_datetime(merged_df['ath_date_now'])
        .astype(int) / 10**9) / 3600, 2)

        # 7. calculate a target called price_diff in percentage
        merged_df['price_diff_percentage'] = round((merged_df['future_price'] - merged_df['price_now']) / merged_df['price_now'] * 100, 2)

        # 8. filter out rows where price_now or future_price is NaN
        filtered_df = merged_df.dropna(subset=['price_now', 'future_price'])

        # 9. sort filtered_df by date_and_hour
        sorted_df = filtered_df.sort_values(by='date_and_hour')

        return sorted_df

    async def add_currency_prices_to_sentiment_data(self,
                                                    extracted_sentiments: pd.DataFrame,
                                                    start_date: int,
                                                    end_date: int,
                                                    prediction_hour_interval: int = 12):
        # Get the latest currency prices
        currency_prices_data = await self.currency_prices_service.get_currency_prices_by_date_range_service(
            start_date=start_date,
            end_date=end_date
        )
        # Convert the currency prices to a DataFrame
        currency_prices = pd.DataFrame([price.model_dump() for price in currency_prices_data])
        # create a field in extracted_sentiments which gets date and hour from created_date_utc_y and call it date_and_hour
        extracted_sentiments['date_and_hour'] = extracted_sentiments['created_utc_y'].dt.strftime('%Y-%m-%d %H:00')
        # from currency_prices timestamp (unix string) get date and hour from created_date_utc_y and call it date_and_hour
        currency_prices['date_and_hour'] = pd.to_datetime(currency_prices['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:00')

        # Ensure datetime columns are datetime
        extracted_sentiments['date_and_hour'] = pd.to_datetime(extracted_sentiments['date_and_hour'])
        currency_prices['date_and_hour'] = pd.to_datetime(currency_prices['date_and_hour'])

        # call add_price_now_and_future_price to add price_now and future_price to extracted_sentiments
        merged_df = self.add_price_now_and_future_price(
            extracted_sentiments=extracted_sentiments,
            currency_prices=currency_prices,
            prediction_hour_interval=prediction_hour_interval
        )
        return merged_df

    
    def add_price_now_and_future_price(self,
                                       extracted_sentiments: pd.DataFrame,
                                       currency_prices: pd.DataFrame,
                                       prediction_hour_interval: int = 12):
        # 1. Prepare "price_now" data with extra fields
        price_now_df = currency_prices[[
            'currency', 'date_and_hour', 'price', 'market_cap', 'total_volume',
            'total_supply', 'ath', 'ath_date'
        ]].copy()
        price_now_df.rename(columns={
            'price': 'price_now',
            'market_cap': 'market_cap_now',
            'total_volume': 'total_volume_now',
            'total_supply': 'total_supply_now',
            'ath': 'ath_now',
            'ath_date': 'ath_date_now'
        }, inplace=True)

        # 2. Prepare "future_price" data with extra fields
        future_price_df = currency_prices[[
            'currency', 'date_and_hour', 'price', 'market_cap', 'total_volume',
            'total_supply', 'ath', 'ath_date'
        ]].copy()
        future_price_df['date_and_hour'] = future_price_df['date_and_hour'] - pd.Timedelta(hours=prediction_hour_interval)
        future_price_df.rename(columns={
            'price': 'future_price',
            'market_cap': 'market_cap_future',
            'total_volume': 'total_volume_future',
            'total_supply': 'total_supply_future',
            'ath': 'ath_future',
            'ath_date': 'ath_date_future'
        }, inplace=True)

        # 3. Expand cohere_df to all currencies
        sentiments_expanded = extracted_sentiments.merge(currency_prices[['currency']].drop_duplicates(), how='cross')

        # 4. Merge to get price_now and metadata
        merged_df = sentiments_expanded.merge(
            price_now_df,
            on=['currency', 'date_and_hour'],
            how='left'
        )

        # 5. Merge to get future_price and metadata
        merged_df = merged_df.merge(
            future_price_df,
            on=['currency', 'date_and_hour'],
            how='left'
        )
        return merged_df

    async def predict_currency_sentiment(self, currency: str, data_df: pd.DataFrame, prediction_interval: str = "12h"):
        # TODO: IMPLEMENT filter data_df for the currency
        currency_df = data_df[data_df['currency'] == currency]