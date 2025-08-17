import logging
import numpy as np
import cv2

logger = logging.getLogger(__name__)

def validate_image(image_file):
    """Validate uploaded image file"""
    try:
        # Store original position
        original_position = image_file.tell()
        
        # Check if file is empty
        if image_file.filename == '':
            return False, "No file selected"
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        file_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        
        if file_ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        # Check if file is actually an image
        file_content = image_file.read()
        if len(file_content) == 0:
            return False, "Empty file provided"
            
        image_array = np.frombuffer(file_content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Reset file pointer to original position
        image_file.seek(original_position)
        
        if image is None:
            return False, "Invalid image format or corrupted file"
        
        return True, "Valid image file"
    
    except Exception as e:
        logger.error(f"Image validation error: {str(e)}")
        # Ensure file pointer is reset even on error
        try:
            image_file.seek(0)
        except:
            pass
        return False, f"Validation error: {str(e)}"

def format_detection_results(detections, model_info, processing_time, request_id, image_shape):
    """Format detection results into structured response"""
    return {
        'success': True,
        'request_id': request_id,
        'detections': detections,
        'total_objects': len(detections),
        'processing_time_ms': processing_time,
        'model_info': model_info,
        'image_info': {
            'width': int(image_shape[1]),
            'height': int(image_shape[0]),
            'channels': int(image_shape[2])
        }
    }