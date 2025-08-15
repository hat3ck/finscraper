from datetime import datetime
import pandas as pd
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
from app.services.llmService import LLMService
from app.services.currencyPricesService import CurrencyPricesService
from app.settings.settings import get_settings
from app.schemas.ml_models import MLModel, MLModelCreate, PreparedSentimentData
from app.schemas.predictions import PredictionsCreate
from app.helper.mlModels import get_active_ml_model, create_ml_models
from app.helper.predictions import create_predictions
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

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

    async def create_ml_models(self, ml_models_create: list[MLModelCreate]):
        ml_models = await create_ml_models(
            session=self.session,
            ml_models_create=ml_models_create
        )
        return ml_models

    async def predict_currencies_sentiment_service(self, prediction_hour_interval: int = 12):
        try:
            # Get a list of currencies to predict
            currencies = self.settings.currency_list
            # get reddit posts, comments, and sentiments from the beginning of 2025 till now
            start_date = int(datetime(2025, 1, 1).timestamp())
            end_date = int(datetime.now().timestamp())
            # prepare sentiment data
            prepared_data = await self.prepare_sentiment_data(
                start_date=start_date,
                end_date=end_date,
                prediction_hour_interval=prediction_hour_interval
            )
            # DataFrame for the last hour data
            last_hour_data = prepared_data.last_hour_data
            # DataFrame for the train data
            train_data = prepared_data.train_data

            # predictions are a list of PredictionsCreate objects
            predictions = []
            for currency in currencies:
                try:
                    # Predict the price for each currency
                    prediction = await self.predict_currency_price(
                        prepared_df=train_data,
                        prediction_df=last_hour_data,
                        currency=currency,
                        hour_interval=prediction_hour_interval
                    )
                    predictions.append(prediction)
                except Exception as e:
                    print(f"Error predicting price for {currency}: {str(e)}; location dI3Dbg4Huw")
                    continue
            if not predictions:
                raise ValueError("No predictions were made for any currency; location s94HgkLp3")
            # Save predictions to the database
            await create_predictions(session=self.session, prediction_create=predictions)
            await self.session.commit()
            return f"Predictions for {len(predictions)} currencies created successfully."
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to predict currencies sentiment: {str(e)}") from e

    async def predict_currency_price(self, prepared_df: pd.DataFrame, prediction_df: pd.DataFrame, currency: str, hour_interval: int = 12):
        # find an ML model for the currency
        ml_model = await self.get_active_ml_model(prediction_currency=currency)
        loaded_model = await self.setup_ml_model(ml_model)
        # get the current price of the currency and convert it to a float
        current_price = float(prepared_df[prepared_df['currency'] == currency]['price_now'].iloc[0])
        # select a subset of the DataFrame for the currency based on model's features and target
        fields_to_use = ml_model.categorical_features + ml_model.numeric_features + [ml_model.target_variable]
        currency_df = prepared_df[prepared_df['currency'] == currency][fields_to_use].reset_index(drop=True)
        currency_prediction_df = prediction_df[prediction_df['currency'] == currency][fields_to_use].reset_index(drop=True)
        if currency_df.empty or currency_prediction_df.empty:
            raise ValueError(f"No data available for currency: {currency}; location j4bf86U5gC")
        X = currency_df.drop(columns=[ml_model.target_variable])
        y = currency_df[ml_model.target_variable]

        X_test = currency_prediction_df.drop(columns=[ml_model.target_variable])

        # Pre-process the data
        X_transformed, X_pred_transformed = await self.preprocess_data_and_prediction_df(ml_model, X, X_test)
                
        # Fit the model
        loaded_model.fit(X_transformed, y)

        # Make predictions
        predictions = loaded_model.predict(X_pred_transformed)

        mean_prediction = None
        # get the mean of the predictions and try to convert to a float
        try:
            mean_prediction = float(predictions.mean())
        except Exception as e:
            raise ValueError(f"Failed to convert predictions to float: {str(e)}; location nsE65tBfK")
        if mean_prediction is None:
            raise ValueError(f"No predictions made for currency: {currency}; location jd2uNjgfp5")
        
        # Calculate the future price based on the current price and the mean prediction
        future_price = current_price * (1 + mean_prediction / 100)

        # prediction timestamp is now plus added hours as interval in unix timestamp
        current_time = int(datetime.now().timestamp())
        prediction_timestamp = int(current_time + (hour_interval * 3600))

        # Create a PredictionsCreate object
        prediction_obj = PredictionsCreate(
            currency=currency,
            priced_in= self.settings.main_currency,
            currency_price=current_price,
            model_provider= ml_model.provider,
            model= ml_model.model,
            predicted_price= future_price,
            prediction_timestamp= prediction_timestamp,
            created_utc= current_time
        )

        return prediction_obj

    async def preprocess_data_and_prediction_df(self, ml_model: MLModel, X: pd.DataFrame, X_test: pd.DataFrame):
        # Define transformers
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, ml_model.numeric_features),
                ('cat', categorical_transformer, ml_model.categorical_features)
            ]
        )
        # Fit and transform X
        X_transformed = preprocessor.fit_transform(X)
        # Transform the prediction DataFrame
        X_pred_transformed = preprocessor.transform(X_test)

        return X_transformed, X_pred_transformed

    async def setup_ml_model(self, ml_model: MLModel):
        match ml_model.provider:
            case "xgboost":
                match ml_model.model:
                    case "XGBRegressor":
                        return XGBRegressor(**ml_model.hyperparameters)
                    case _:
                        raise ValueError(f"Unsupported XGBoost model: {ml_model.model}; location Rb2Z8uLWg6")
            case _:
                raise ValueError(f"Unsupported ML model provider: {ml_model.provider}; location 7uBsE6A3gB")

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

        # 8. sort filtered_df by date_and_hour
        sorted_df = merged_df.sort_values(by='date_and_hour')

        # 9. get the last hour for prediction of the next interval hours
        last_hour = sorted_df['date_and_hour'].max()
        last_hour_df = sorted_df[sorted_df['date_and_hour'] == last_hour]
        # if there are no rows in last_hour_df, there is nothing to predict so raise an error
        if last_hour_df.empty:
            raise ValueError("No data available for the last hour to predict future prices. location Sbt03LN2bR")

        # 10. filter out rows where price_now or future_price is NaN
        filtered_df = sorted_df.dropna(subset=['price_now', 'future_price'])

        prepared_data = PreparedSentimentData(
            train_data=filtered_df,
            last_hour_data=last_hour_df
        )
        return prepared_data

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