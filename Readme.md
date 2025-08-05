# How to update models with alembic?

```bash
DB_HOST=[DB_HOST] DB_USER=[DB_USER] DB_PORT=[DB_PORT] DB_PASSWORD=[DB_PASSWORD] DB_NAME=[DB_NAME]  REDDIT_CLIENT_ID=[REDDIT_CLIENT_ID] REDDIT_CLIENT_SECRET=[REDDIT_CLIENT_SECRET] alembic revision --autogenerate -m "MESSAGE"
DB_HOST=[DB_HOST] DB_USER=[DB_USER] DB_PORT=[DB_PORT] DB_PASSWORD=[DB_PASSWORD] DB_NAME=[DB_NAME]
REDDIT_CLIENT_ID=[REDDIT_CLIENT_ID] REDDIT_CLIENT_SECRET=[REDDIT_CLIENT_SECRET] COINGECKO_API_KEY=[COINGECKO_API_KEY] alembic upgrade head
```

# How to create docker image?

```bash
docker build -t finscraper:[VERSION] .
```

# How to update docker image?

```bash

        docker login ghcr.io -u [USERNAME] -p [ACCESS_TOKEN]
        docker tag finscraper:[VERSION] ghcr.io/hat3ck/finscraper:[VERSION]
        docker push ghcr.io/hat3ck/finscraper:[VERSION]
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
    -p 8000:8000 \
    ghcr.io/hat3ck/finscraper:[VERSION]
```
