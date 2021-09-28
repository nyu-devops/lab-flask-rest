# Image for a Python 3 development environment 
FROM python:3.9-slim

# Add any tools that are needed beyond Python 3.9
RUN apt update && \
    apt install -y sudo git tree wget build-essential libpq-dev

# Set up the development environment
WORKDIR /workspace

COPY requirements.txt .
RUN pip install -U pip && \
    pip install wheel && \
    pip install -r requirements.txt

# Create a user for development
ARG USERNAME=devops
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN useradd --uid $USER_UID -m $USERNAME -s /bin/bash && \
    usermod -aG sudo $USERNAME && \
    echo "$USERNAME ALL=\(root\) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME
    
# Become a regular user
USER devops

EXPOSE 5000

