# Use an official Python runtime as a parent image
# Using a specific version is good practice for reproducibility
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

ENV PYTHONPATH=/app

# Copy the requirements file into the container at /app
# This is done first to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir keeps the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application's code into the container
COPY src/ ./src
COPY strategy_documents/ ./strategy_documents
COPY tests/ ./tests

# This container will run scripts on-demand.
# The command will be provided when we run the container.
# For example: `python src/suggest_content.py`
