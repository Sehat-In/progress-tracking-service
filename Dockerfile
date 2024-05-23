FROM python:3.9

WORKDIR /code

ARG DATABASE_HOST
ARG DATABASE_NAME
ARG DATABASE_PORT
ARG DATABASE_USER
ARG DATABASE_PASSWORD

ENV DATABASE_HOST ${DATABASE_HOST}
ENV DATABASE_NAME ${DATABASE_NAME}
ENV DATABASE_PORT ${DATABASE_PORT}
ENV DATABASE_USER ${DATABASE_USER}
ENV DATABASE_PASSWORD ${DATABASE_PASSWORD}

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 3002

CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--port", "3002"]