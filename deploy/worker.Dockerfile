# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY setup.py setup.py
RUN pip3 install -e .
COPY . .
CMD [ "python3", "worker.py"]
