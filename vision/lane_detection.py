import cv2
import numpy as np
from .camera_utils import Camera

class LaneDetector:
    def __init__(self):
        """
        Initialize lane detector
        """
        self.camera = Camera()
        
    def detect_lanes(self, frame=None):
        """
        Detect lanes in the given frame
        Args:
            frame: Input frame (if None, captures from camera)
        Returns:
            tuple: (left_lane, right_lane) coordinates and visualization frame
        """
        if frame is None:
            frame = self.camera.get_frame()
            
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blur, 50, 150)
        
        # Define region of interest
        height, width = frame.shape[:2]
        roi_vertices = np.array([
            [(0, height),
             (width/4, height/2),
             (3*width/4, height/2),
             (width, height)]
        ], dtype=np.int32)
        
        # Create mask for region of interest
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, roi_vertices, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(
            masked_edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=100,
            maxLineGap=50
        )
        
        # Separate left and right lane lines
        left_lines = []
        right_lines = []
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                
                if slope < 0:  # Left lane
                    left_lines.append(line[0])
                else:  # Right lane
                    right_lines.append(line[0])
                    
        # Average the lines
        left_lane = self._average_lines(left_lines, height)
        right_lane = self._average_lines(right_lines, height)
        
        # Create visualization
        visualization = frame.copy()
        if left_lane is not None:
            cv2.line(visualization, left_lane[0], left_lane[1], (0, 255, 0), 3)
        if right_lane is not None:
            cv2.line(visualization, right_lane[0], right_lane[1], (0, 255, 0), 3)
            
        return (left_lane, right_lane), visualization
        
    def _average_lines(self, lines, height):
        """
        Average multiple lines into a single line
        Args:
            lines: List of line coordinates
            height: Image height
        Returns:
            tuple: Averaged line coordinates
        """
        if not lines:
            return None
            
        # Convert lines to slope-intercept form
        slopes = []
        intercepts = []
        
        for line in lines:
            x1, y1, x2, y2 = line
            if x2 == x1:
                continue
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            slopes.append(slope)
            intercepts.append(intercept)
            
        if not slopes:
            return None
            
        # Average slope and intercept
        avg_slope = np.mean(slopes)
        avg_intercept = np.mean(intercepts)
        
        # Calculate endpoints
        y1 = height
        y2 = int(height/2)
        x1 = int((y1 - avg_intercept) / avg_slope)
        x2 = int((y2 - avg_intercept) / avg_slope)
        
        return ((x1, y1), (x2, y2))
        
    def __del__(self):
        self.camera.release() 