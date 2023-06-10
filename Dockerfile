# Dockerfile used as bulding the docker image used in the nodes
# Start with a base image containing Python runtime
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1
ENV GITHUB_API_TOKEN=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
ENV TERMINATE_AFTER_N_MESSAGES=10
# The maintainer email
LABEL maintainer="gustavfredrikson@gmail.com"

# Set the working directory in the Docker image
WORKDIR /app


# Install system level dependencies for pycairo and systemd
RUN apt-get update && apt-get install -y \
    python3-dev \
    libcairo2-dev \
    libffi-dev \
    build-essential \
    pkg-config \
    libsystemd-dev

ENV PYTHONUNBUFFERED=1
# Install any needed packages specified in requirements.txt
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

