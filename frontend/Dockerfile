FROM --platform=linux/amd64 python:3.10-slim as build

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install dependencies first (for better caching)
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY frontend/app.py /app/
COPY frontend/static/ /app/static/

# Expose the Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]