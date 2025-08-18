#!/bin/bash

# Object Detection Microservice Start Script

echo "🚀 Starting Object Detection Microservice..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p outputs test_images

# Create .env files if they don't exist
if [ ! -f ai-backend/.env ]; then
    echo "Creating AI backend .env file..."
    cat > ai-backend/.env << EOL
FLASK_ENV=production
MODEL_NAME=yolo11n.pt
CONFIDENCE_THRESHOLD=0.25
MAX_IMAGE_SIZE=16777216
LOG_LEVEL=INFO
EOL
fi

if [ ! -f ui-backend/.env ]; then
    echo "Creating UI backend .env file..."
    cat > ui-backend/.env << EOL
FLASK_ENV=production
AI_BACKEND_URL=http://127.0.0.1:5001
MAX_CONTENT_LENGTH=16777216
UPLOAD_TIMEOUT=30
LOG_LEVEL=INFO
EOL
fi

# Build and start the services
echo "🔨 Building and starting services..."
docker-compose up --build

# If the script reaches here, it means the services were stopped
echo "🛑 Services stopped."