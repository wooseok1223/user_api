FROM python:3.8

WORKDIR /user_api

ENV PYTHONUNBUFFERED=1

ADD . .
RUN pip install -r requirements.txt
