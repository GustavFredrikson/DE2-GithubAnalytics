# Dockerfile used as bulding the docker image used in the nodes
# Start with a base image containing Python runtime
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1
# The maintainer email
LABEL maintainer="gustavfredrikson@gmail.com"

# Set the working directory in the Docker image
WORKDIR /tmp


ADD requirements.txt /tmp

# Install system level dependencies for pycairo and systemd
RUN apt-get update && apt-get install -y \
    python3-dev \
    libcairo2-dev \
    libffi-dev \
    build-essential \
    pkg-config \
    libsystemd-dev

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
