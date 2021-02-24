# Image for a Python 3 development environment 
FROM python:3.8-slim

# Add any tools that are needed beyond Python 3.8
RUN apt update && apt install -y sudo git tree wget build-essential libpq-dev

# Create a user for development
RUN useradd devops -m -s /bin/bash && \
    usermod -aG sudo devops && \
    echo "devops   ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/devops

# Set up the development emvironment
WORKDIR /workspace

COPY requirements.txt .
RUN pip install -U pip && \
    pip install -r requirements.txt

EXPOSE 5000

# Become a regular user
USER devops
