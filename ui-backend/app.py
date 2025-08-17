from flask import Flask, request, render_template, jsonify, send_from_directory
import requests
import os
import json
import uuid
from werkzeug.utils import secure_filename
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour", "5 per minute"]
)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Backend configuration
AI_BACKEND_URL = os.getenv('AI_BACKEND_URL', 'http://127.0.0.1:5001')

print("AI_BACKEND_URL: ", AI_BACKEND_URL)


AI_BACKEND_TIMEOUT = int(os.getenv('UPLOAD_TIMEOUT', 30))

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_file(file):
    """Validate uploaded image file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, "Valid file"

@app.route('/')
def index():
    """Serve main upload interface"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # Limit detection requests
def upload_and_detect():
    """Handle image upload and trigger detection"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'error_code': 'NO_IMAGE_FILE'
            }), 400
        
        file = request.files['image']
        is_valid, message = validate_image_file(file)
        
        if not is_valid:
            return jsonify({
                'error': message,
                'error_code': 'INVALID_FILE'
            }), 400
        
        # Generate unique request ID for tracking
        request_id = str(uuid.uuid4())
        logger.info(f"Processing request {request_id} for file: {file.filename}")
        
        # Prepare file for AI backend
        files = {
            'image': (file.filename, file.read(), file.content_type)
        }
        
        # Bridge to AI Backend
        detection_result = call_ai_backend(files, request_id)
        
        if detection_result['success']:
            logger.info(f"Request {request_id} completed successfully")
            return jsonify({
                'success': True,
                'request_id': request_id,
                'filename': secure_filename(file.filename),
                'results': detection_result['data']
            })
        else:
            logger.error(f"Request {request_id} failed: {detection_result['error']}")
            return jsonify({
                'success': False,
                'error': detection_result['error'],
                'error_code': detection_result.get('error_code', 'UNKNOWN_ERROR')
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500

def call_ai_backend(files, request_id):
    """Communication bridge to AI Backend"""
    try:
        logger.info(f"Calling AI backend for request {request_id}")
        
        # Make request to AI backend
        response = requests.post(
            f"{AI_BACKEND_URL}/detect",
            files=files,
            headers={'X-Request-ID': request_id},
            timeout=AI_BACKEND_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"AI backend responded successfully for {request_id}")
            return {'success': True, 'data': data}
        else:
            error_msg = f"AI backend error: {response.status_code}"
            error_code = 'AI_BACKEND_ERROR'
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_msg)
                error_code = error_data.get('error_code', error_code)
            except:
                pass
            
            return {'success': False, 'error': error_msg, 'error_code': error_code}
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'AI backend timeout - processing took too long', 'error_code': 'AI_TIMEOUT'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'AI backend unavailable - service may be down', 'error_code': 'AI_UNAVAILABLE'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Communication error: {str(e)}', 'error_code': 'COMMUNICATION_ERROR'}

@app.route('/health')
def health_check():
    """Health check endpoint"""
    # Also check AI backend health
    try:
        response = requests.get(f"{AI_BACKEND_URL}/health", timeout=5)
        ai_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        ai_status = "unreachable"
    
    return jsonify({
        'service': 'ui-backend',
        'status': 'healthy',
        'ai_backend_status': ai_status,
        'timestamp': '2025-08-16T15:42:00'
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)