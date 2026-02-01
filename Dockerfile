# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for Scapy sniffing)
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create the logs directory
RUN mkdir -p logs

# Run the application (by default, runs the engine)
CMD ["python", "main.py"]