import cv2
import numpy as np
from .camera_utils import Camera

class ObjectDetector:
    def __init__(self):
        """
        Initialize object detector with YOLO model
        """
        # Load YOLO model
        self.net = cv2.dnn.readNet(
            "vision/models/yolov3.weights",
            "vision/models/yolov3.cfg"
        )
        
        # Load COCO class names
        with open("vision/models/coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
            
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        self.camera = Camera()
        
    def detect_objects(self, frame=None):
        """
        Detect objects in the given frame
        Args:
            frame: Input frame (if None, captures from camera)
        Returns:
            list: List of detected objects with their positions
        """
        if frame is None:
            frame = self.camera.get_frame()
            
        height, width = frame.shape[:2]
        
        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(
            frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False
        )
        
        # Detect objects
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)
        
        # Process detections
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:  # Confidence threshold
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    
        # Apply non-maximum suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        # Prepare results
        results = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                results.append({
                    'class': self.classes[class_ids[i]],
                    'confidence': confidences[i],
                    'box': (x, y, w, h)
                })
                
        return results
        
    def __del__(self):
        self.camera.release() 