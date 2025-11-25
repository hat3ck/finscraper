# About
## Cryptocurrency price prediction based on Sentiment Analysis from Reddit using LLMs and Machine Learning.
* This application will fetch reddit topics and comments related to cryptocurrencies.
* Subsequently, it will call a Large Language Model (in this case Cohere models) to label the comments and topics.
* Also, it will fetch the price of top 20 crypto currencies.
* Once enough data is gathered, it will utilize extracted sentiments with their historcial data to provide a prediction of the currency price for the future using Machine Learning models (XGBoost for now).

## Supported cryptocurrencies
["btc", "eth", "usdt", "bnb", "xrp", "ada", "sol", "usdc", "doge", "steth", "sui", "trx", "link", "leo", "avax", "xlm", "ton", "shib", "ltc", "xmr", "bgb", "pi", "uni"]

## Supported subreddits
["CryptoCurrency", "Bitcoin", "CryptoMarkets", "BitcoinMarkets", "Altcoin", "CryptoTechnology", "CryptoCurrencyTrading", "CryptoNews"]

## OPENAPI Documentation
Once the application is running, you can access the OpenAPI documentation at: `http://[APP_HOST]:[APP_PORT]/api/docs`

## Requirements
- Python 3.9+
- Postgres database
- Reddit developer account with client ID and secret
- Coingecko API key
- Cohere API key

# How to run?
Here are the steps to set up and run the application locally:
## Get a reddit developer account
You can find more information about creating a reddit developer account here: https://www.reddit.com/r/reddit.com/wiki/api/
## Get a coingecko API key
You can find more information about creating a coingecko API key here: https://www.coingecko.com/en/api
## Get a cohere API key
You can find more information about creating a cohere API key here: https://cohere.com
## Setup a Postgres database
You can use any Postgres database. Make sure to create a database and a user with all privileges to the database.

## How to run the app locally?
1- create a .env file in the root directory of the project with the following content:

```env
ENV=[ENV]
APP_PORT=[APP_PORT]
DB_HOST=[DB_HOST]
DB_USER=[DB_USER]
DB_PORT=[DB_PORT]
DB_PASSWORD=[DB_PASSWORD]
DB_NAME=[DB_NAME]
REDDIT_CLIENT_ID=[REDDIT_CLIENT_ID]
REDDIT_CLIENT_SECRET=[REDDIT_CLIENT_SECRET]
COINGECKO_API_KEY=[COINGECKO_API_KEY]
COHERE_API_KEY=[COHERE_API_KEY]
```
2- install the dependencies:

```bash
pip install -r requirements.txt
```
3- run the alembic migrations:<br/>
Alembic is used for database migrations. The configuration file is located at `alembic.ini`, and the migration scripts are located in the `app/alembic/versions` directory.<br/>
To create a new migration file or to apply the migrations, use the following commands:

```bash
DB_HOST=[DB_HOST] DB_USER=[DB_USER] DB_PORT=[DB_PORT] DB_PASSWORD=[DB_PASSWORD] DB_NAME=[DB_NAME]  REDDIT_CLIENT_ID=[REDDIT_CLIENT_ID] REDDIT_CLIENT_SECRET=[REDDIT_CLIENT_SECRET] alembic revision --autogenerate -m "MESSAGE"
DB_HOST=[DB_HOST] DB_USER=[DB_USER] DB_PORT=[DB_PORT] DB_PASSWORD=[DB_PASSWORD] DB_NAME=[DB_NAME]
REDDIT_CLIENT_ID=[REDDIT_CLIENT_ID] REDDIT_CLIENT_SECRET=[REDDIT_CLIENT_SECRET] COINGECKO_API_KEY=[COINGECKO_API_KEY] alembic upgrade head
```

4- run the application:

```bash
uvicorn app.main:app --host
```

# How to use the application?
Once the application is running, you can use the following endpoints:
- `GET /api/reddit_posts/fetch_posts_and_comments`: Fetch reddit posts and comments related to cryptocurrencies.
- `GET /api/currency_prices`: Fetch the price of top 20 crypto currencies.
- `GET /api/llm/reddit_sentiments_by_date_range`: Label the comments and topics using Cohere models for a given date range.
- `POST /api/ml/predict`: Creates a new hourly prediction for currencies based on ML models set up for each currency. There is an hour_interval parameter to specify the exact hour to predict.

# labeling comments and posts using LLMs
To call the llm to label the comments and posts, you need to add a document in the 'llm_providers' collection in the database like the example below:

```json
[
 {
   "id": 3,
   "name": "cohere",
   "model": "command-r7b-12-2024",
   "default_api_key": "YOUR_COHERE_API_KEY",
   "api_url": "https://api.cohere.com/v2",
   "tokens_per_minute": 128000,
   "calls_per_minute": 20,
   "total_used_tokens": 0,
   "is_active": true,
   "created_at": 1754069817,
   "access_token": null,
   "access_token_expiry": null,
   "access_token_type": null
 }
]
```

# Prediction model setup
To set up the prediction models for each currency, you need to create a document in 'ml_models' collection in the database for each currency like the example below:

```json
[
 {
   "id": 5,
   "name": "btc_usd_model",
   "prediction_currency": "btc",
   "description": "Predicts BTC price in USD based on Reddit sentiment and market data.",
   "provider": "xgboost",
   "model": "XGBRegressor",
   "model_type": "regression",
   "hyperparameters": "{\"objective\": \"reg:squarederror\", \"colsample_bytree\": 1.0, \"enable_categorical\": false, \"gamma\": 0, \"learning_rate\": 0.1, \"max_depth\": 7, \"n_estimators\": 200, \"random_state\": 42, \"reg_alpha\": 0, \"reg_lambda\": 1, \"subsample\": 1.0}",
   "numeric_features": "[\"score_x\", \"score_y\", \"depth\", \"market_cap_now\", \"total_volume_now\", \"total_supply_now\", \"hours_since_ath\"]",
   "categorical_features": "[\"crypto_sentiment\", \"future_sentiment\", \"emotion\", \"subjective\"]",
   "target_variable": "price_diff_percentage",
   "created_utc": 1754971403,
   "updated_utc": 1754971403,
   "is_active": true
 }
]
```

# How to run tests?

You will need to create a .env file in app/tests/integration with a similar content as the .env file in the root directory. The only difference is that you should use a different database and api keys for testing to avoid any conflicts with the development data because the database will be wiped during the tests.
```bash
pytest app/tests/integration
```

# How to create docker image?

```bash
docker build -t finscraper:[VERSION] .
```

# How to update docker image?

```bash

        docker login ghcr.io -u [USERNAME] -p [ACCESS_TOKEN]
        docker tag finscraper:[VERSION] ghcr.io/[USERNAME]/finscraper:[VERSION]
        docker push ghcr.io/[USERNAME]/finscraper:[VERSION]
```

# How to run the app from docker?

```bash
docker run -d --name finscraper \
    -e ENV=[ENV] \
    -e APP_PORT=[APP_PORT] \
    -e DB_HOST=[DB_HOST] \
    -e DB_USER=[DB_USER] \
    -e DB_PORT=[DB_PORT] \
    -e DB_PASSWORD=[DB_PASSWORD] \
    -e DB_NAME=[DB_NAME] \
    -e REDDIT_CLIENT_ID=[REDDIT_CLIENT_ID] \
    -e REDDIT_CLIENT_SECRET=[REDDIT_CLIENT_SECRET] \
    -e COINGECKO_API_KEY=[COINGECKO_API_KEY] \
    -e COHERE_API_KEY=[COHERE_API_KEY] \
    -p 8000:8000 \
    ghcr.io/[USERNAME]/finscraper:[VERSION]
```
