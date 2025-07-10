# How to update models with alembic?

```bash
DB_HOST=[DB_HOST] DB_USER=[DB_USER] DB_PORT=[DB_PORT] DB_PASSWORD=[DB_PASSWORD] DB_NAME=[DB_NAME] alembic revision --autogenerate -m "MESSAGE"
DB_HOST=[DB_HOST] DB_USER=[DB_USER] DB_PORT=[DB_PORT] DB_PASSWORD=[DB_PASSWORD] DB_NAME=[DB_NAME] alembic upgrade head
```
