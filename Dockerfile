FROM python:3.11-slim

WORKDIR /finscraper

COPY ./requirements.txt /finscraper/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /finscraper/requirements.txt

COPY ./app /finscraper/app

ENV APP_PORT=80
CMD sh -c "fastapi run app/main.py --port \${APP_PORT:-80} --workers 4"