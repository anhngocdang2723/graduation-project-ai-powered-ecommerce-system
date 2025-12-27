FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Make init script executable
RUN chmod +x init_db.sh

# Expose port
EXPOSE 8001

# Run database initialization then start application
CMD ["sh", "-c", "./init_db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"]
