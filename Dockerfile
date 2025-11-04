FROM python:3.12-slim

LABEL version="1.0.9" \
      description="Update tests and use python 3.12" \
      release.date="2025-11-04"

WORKDIR /finscraper

COPY ./requirements.txt /finscraper/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /finscraper/requirements.txt

COPY ./app /finscraper/app

ENV APP_PORT=80
CMD sh -c "fastapi run app/main.py --port \${APP_PORT:-80} --workers 4"