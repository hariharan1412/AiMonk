from flask import Flask, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import logging
import time
import os
import uuid
from detector import ObjectDetector
from utils import validate_image, format_detection_results

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize detector
detector = None

def initialize_detector():
    """Initialize YOLO detector with error handling"""
    global detector
    try:
        logger.info("Initializing YOLOv11 nano detector...")
        detector = ObjectDetector(model_name='yolo11n.pt')
        logger.info("Detector initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize detector: {str(e)}")
        return False

@app.route('/detect', methods=['POST'])
def detect_objects():
    """Main detection endpoint"""
    start_time = time.time()
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    logger.info(f"Processing detection request {request_id}")
    
    try:
        # Check if model is loaded
        if not detector or not detector.is_ready():
            return jsonify({
                'error': 'AI model not ready',
                'error_code': 'MODEL_NOT_LOADED'
            }), 503
        
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'error_code': 'NO_IMAGE_FILE'
            }), 400
        
        image_file = request.files['image']
        
        # Check file size (16MB limit)
        image_file.seek(0, os.SEEK_END)
        file_size = image_file.tell()
        image_file.seek(0)
        
        if file_size > 16 * 1024 * 1024:
            return jsonify({
                'error': 'Image file too large (max 16MB)',
                'error_code': 'FILE_TOO_LARGE'
            }), 413
        
        # Validate image
        is_valid, error_msg = validate_image(image_file)
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'error_code': 'INVALID_IMAGE'
            }), 400
        
        # Convert to OpenCV format
        image_array = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({
                'error': 'Invalid image format or corrupted file',
                'error_code': 'INVALID_IMAGE_FORMAT'
            }), 400
        
        # Perform detection
        logger.info(f"Running detection for request {request_id}")
        detections, model_info = detector.detect(image)
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000, 2)  # ms
        
        # Format results
        result = format_detection_results(
            detections=detections,
            model_info=model_info,
            processing_time=processing_time,
            request_id=request_id,
            image_shape=image.shape
        )
        
        logger.info(f"Request {request_id} completed in {processing_time}ms - found {len(detections)} objects")
        
        return jsonify(result)
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Detection failed for request {request_id}: {str(e)}")
        return jsonify({
            'error': f'Detection processing failed: {str(e)}',
            'error_code': 'DETECTION_FAILED',
            'processing_time_ms': processing_time
        }), 500

@app.route('/health')
def health_check():
    """Health check with model status"""
    model_status = "loaded" if detector and detector.is_ready() else "not_loaded"
    
    return jsonify({
        'service': 'ai-backend',
        'status': 'healthy',
        'model_status': model_status,
        'model_name': 'YOLOv11 Nano',
        'coco_classes_count': 80,
        'timestamp': '2025-08-16T15:42:00'
    })

@app.route('/model/info')
def model_info():
    """Get detailed model information"""
    if not detector:
        return jsonify({
            'error': 'Model not loaded',
            'error_code': 'MODEL_NOT_LOADED'
        }), 503
    
    return jsonify(detector.get_model_info())

if __name__ == '__main__':
    # Initialize detector on startup
    if not initialize_detector():
        logger.critical("Failed to initialize detector - exiting")
        exit(1)
    
    app.run(host='0.0.0.0', port=5001, debug=False)