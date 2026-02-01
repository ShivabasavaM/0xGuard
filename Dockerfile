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
# (This includes main.py, dashboard.py, tools/, models/, etc.)
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create the logs directory (Best practice to ensure it exists)
RUN mkdir -p logs

# Expose the Streamlit port so the user can access the UI
EXPOSE 8501

# Make the start script executable
RUN chmod +x start.sh

# Run the wrapper script to start BOTH the Guard and Dashboard
CMD ["./start.sh"]