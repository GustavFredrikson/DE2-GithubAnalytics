# Start with a base image containing Python runtime
FROM python:3.8-slim-buster

# The maintainer email
LABEL maintainer="gustavfredrikson@gmail.com"

# Set the working directory in the Docker image
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

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

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run python when the container launches
CMD ["python", "app.py"]
