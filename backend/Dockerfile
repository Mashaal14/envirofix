FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary requests

# Copy application code
COPY . .

# Run the API
CMD ["uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "7070"]
