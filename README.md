# Object Detection Microservice

A production-ready microservice for object detection using YOLOv11, with a clean web interface and scalable architecture.

## Architecture

The system consists of two main services:

1. **UI Backend** (Port 5000): Handles user interface, file uploads, and communicates with the AI backend
2. **AI Backend** (Port 5001): Handles YOLOv11 model loading and object detection

## Features

- Web-based interface for image uploads
- Real-time object detection using YOLOv11 Nano
- Structured JSON responses with detection results
- Robust error handling and validation
- Docker containerization for easy deployment
- Health check endpoints for monitoring

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Running the Application

1. Clone this repository
2. Navigate to the project directory
3. Run the following command:

```bash
docker-compose up --build


# curl -X POST -F "image=@test_images/sample.jpg" http://localhost:5000/upload