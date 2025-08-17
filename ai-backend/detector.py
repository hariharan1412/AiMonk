from ultralytics import YOLO
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, model_name='yolo11n.pt', confidence_threshold=0.25):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load YOLOv11 model"""
        try:
            logger.info(f"Loading {self.model_name}...")
            self.model = YOLO(self.model_name)
            logger.info(f"Model loaded successfully - {len(self.model.names)} classes available")
            
            # Warmup the model with a dummy image
            self.warmup_model()
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def warmup_model(self):
        """Warmup model with dummy inference"""
        try:
            logger.info("Warming up model...")
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(dummy_image, conf=self.confidence_threshold, verbose=False)
            logger.info("Model warmup completed")
        except Exception as e:
            logger.warning(f"Model warmup failed: {str(e)}")
    
    def is_ready(self):
        """Check if model is ready for inference"""
        return self.model is not None
    
    def detect(self, image):
        """Perform object detection"""
        if not self.is_ready():
            raise RuntimeError("Model not loaded")
        
        # Run inference
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    # Fixed: Access first element of confidence tensor
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls.cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    detection = {
                        'class_id': class_id,
                        'class_name': class_name,
                        'confidence': round(confidence, 4),
                        'bbox': {
                            'x1': int(x1), 'y1': int(y1),
                            'x2': int(x2), 'y2': int(y2),
                            'width': int(x2 - x1),
                            'height': int(y2 - y1),
                            'center_x': int((x1 + x2) / 2),
                            'center_y': int((y1 + y2) / 2)
                        }
                    }
                    detections.append(detection)
        
        model_info = {
            'model_name': self.model_name,
            'total_classes': len(self.model.names),
            'confidence_threshold': self.confidence_threshold
        }
        
        return detections, model_info
    
    def get_model_info(self):
        """Get detailed model information"""
        if not self.is_ready():
            return {'error': 'Model not loaded'}
        
        return {
            'model_name': self.model_name,
            'class_names': list(self.model.names.values()),
            'total_classes': len(self.model.names),
            'confidence_threshold': self.confidence_threshold,
            'input_size': 640  # YOLOv11 default
        }