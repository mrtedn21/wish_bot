# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster
WORKDIR /app
COPY setup.py setup.py
RUN pip3 install -e .
COPY . .
CMD [ "python3", "poller.py"]
