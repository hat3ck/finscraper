FROM python:3.11-slim

LABEL version="1.0.8" \
      description="Refactor fetch reddit posts and comments for llm labeling." \
      release.date="2025-08-22"

WORKDIR /finscraper

COPY ./requirements.txt /finscraper/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /finscraper/requirements.txt

COPY ./app /finscraper/app

ENV APP_PORT=80
CMD sh -c "fastapi run app/main.py --port \${APP_PORT:-80} --workers 4"