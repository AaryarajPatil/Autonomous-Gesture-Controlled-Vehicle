import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self):
        """
        Initialize visualizer
        """
        self.colors = {
            'FORWARD': (0, 255, 0),    # Green
            'BACKWARD': (0, 0, 255),   # Red
            'LEFT': (255, 165, 0),     # Orange
            'RIGHT': (255, 0, 0),      # Blue
            'STOP': (128, 128, 128)    # Gray
        }
        
    def draw_gesture(self, frame: np.ndarray, gesture: str, confidence: float):
        """
        Draw gesture information on frame
        Args:
            frame: Input frame
            gesture: Detected gesture
            confidence: Detection confidence
        """
        # Draw gesture text
        text = f"Gesture: {gesture} ({confidence:.2f})"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    self.colors.get(gesture, (255, 255, 255)), 2)
                    
    def draw_objects(self, frame: np.ndarray, objects: List[Dict[str, Any]]):
        """
        Draw detected objects on frame
        Args:
            frame: Input frame
            objects: List of detected objects
        """
        for obj in objects:
            # Get object properties
            box = obj['box']
            class_name = obj['class']
            confidence = obj['confidence']
            
            # Draw bounding box
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name} ({confidence:.2f})"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
                        
    def draw_lanes(self, frame: np.ndarray, lanes: Tuple[Tuple[Tuple[int, int], Tuple[int, int]], Tuple[Tuple[int, int], Tuple[int, int]]]):
        """
        Draw detected lanes on frame
        Args:
            frame: Input frame
            lanes: Tuple of left and right lane coordinates
        """
        left_lane, right_lane = lanes
        
        # Draw left lane
        if left_lane is not None:
            cv2.line(frame, left_lane[0], left_lane[1], (255, 0, 0), 3)
            
        # Draw right lane
        if right_lane is not None:
            cv2.line(frame, right_lane[0], right_lane[1], (0, 0, 255), 3)
            
    def draw_path(self, frame: np.ndarray, path: List[Tuple[float, float]]):
        """
        Draw planned path on frame
        Args:
            frame: Input frame
            path: List of path waypoints
        """
        if not path:
            return
            
        # Convert waypoints to pixel coordinates
        points = np.array(path, dtype=np.int32)
        
        # Draw path
        cv2.polylines(frame, [points], False, (0, 255, 255), 2)
        
    def draw_terrain(self, frame: np.ndarray, terrain_type: str, features: Dict[str, float]):
        """
        Draw terrain information on frame
        Args:
            frame: Input frame
            terrain_type: Classified terrain type
            features: Terrain features
        """
        # Draw terrain type
        text = f"Terrain: {terrain_type}"
        cv2.putText(frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2)
                    
        # Draw features
        y = 90
        for feature, value in features.items():
            text = f"{feature}: {value:.2f}"
            cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2)
            y += 30
            
    def plot_sensor_data(self, sensor_data: Dict[str, List[float]], title: str = "Sensor Data"):
        """
        Plot sensor data
        Args:
            sensor_data: Dictionary of sensor readings
            title: Plot title
        """
        plt.figure(figsize=(10, 6))
        
        for sensor, data in sensor_data.items():
            plt.plot(data, label=sensor)
            
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def create_dashboard(self, frames: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Create a dashboard with multiple views
        Args:
            frames: Dictionary of frames to display
        Returns:
            Combined dashboard frame
        """
        # Calculate grid dimensions
        n_frames = len(frames)
        n_cols = int(np.ceil(np.sqrt(n_frames)))
        n_rows = int(np.ceil(n_frames / n_cols))
        
        # Create empty dashboard
        frame_height, frame_width = next(iter(frames.values())).shape[:2]
        dashboard = np.zeros((frame_height * n_rows, frame_width * n_cols, 3), dtype=np.uint8)
        
        # Place frames in dashboard
        for i, (name, frame) in enumerate(frames.items()):
            row = i // n_cols
            col = i % n_cols
            
            # Add frame to dashboard
            y1 = row * frame_height
            y2 = (row + 1) * frame_height
            x1 = col * frame_width
            x2 = (col + 1) * frame_width
            dashboard[y1:y2, x1:x2] = frame
            
            # Add frame name
            cv2.putText(dashboard, name, (x1 + 10, y1 + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        
        return dashboard 