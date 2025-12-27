#!/bin/bash

echo "==================================="
echo "Deploying Recommendation Service"
echo "==================================="

# Stop existing containers
echo "Stopping existing containers..."
docker-compose stop recommendation

# Remove old container
echo "Removing old container..."
docker-compose rm -f recommendation

# Build new image
echo "Building recommendation service..."
docker-compose build recommendation

# Start service
echo "Starting recommendation service..."
docker-compose up -d recommendation

# Wait for service to be ready
echo "Waiting for service to be ready..."
sleep 10

# Check if service is running
echo "Checking service health..."
docker-compose ps recommendation

# Check logs
echo -e "\n==================================="
echo "Service Logs (last 20 lines):"
echo "==================================="
docker-compose logs --tail=20 recommendation

# Test health endpoint
echo -e "\n==================================="
echo "Testing health endpoint..."
echo "==================================="
curl -s http://localhost:8001/health | jq .

echo -e "\n==================================="
echo "Deployment complete!"
echo "Service is running at: http://localhost:8001"
echo "API docs at: http://localhost:8001/docs"
echo "==================================="
