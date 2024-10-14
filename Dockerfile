# Use a Python base image
FROM python:3.9-slim

# Sets working directory
WORKDIR /usr/src/app

# Copy requirements.txt file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Expose necesary volumes, for example, a persistent directory
# VOLUME /usr/src/app/html

# Define environment variable for Telegram token
ENV TELEGRAM_TOKEN=<tu_token_telegram>

# Run bot when container starts
CMD ["python", "./bot.py"]
