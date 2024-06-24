# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Update and install dependencies
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y curl zip libvips-dev libvips-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed Python packages
RUN pip install Flask gunicorn

# Copy your application files to the working directory
COPY index.html /app/index.html
COPY statics /app/statics

# Expose port 80 to the outside world
EXPOSE 80

# Define environment variable
ENV FLASK_APP=app.py

# Run Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]
