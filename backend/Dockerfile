FROM --platform=linux/amd64 python:3.10-slim as build

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install dependencies first
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with directory structure
COPY backend/config.py /app/
COPY backend/api.py /app/
COPY backend/agents/ /app/agents/
COPY backend/graph/ /app/graph/

# Expose the API port
EXPOSE 8080

# Command to run the API server
CMD ["python", "api.py"]