import json
import time
from datetime import datetime
from typing import Dict, Any, List
import os

class DataLogger:
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize data logger
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create new log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"car_log_{timestamp}.json")
        
        # Initialize log data
        self.log_data = {
            'start_time': time.time(),
            'events': []
        }
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event with associated data
        Args:
            event_type: Type of event (e.g., 'movement', 'sensor', 'error')
            data: Event data
        """
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'data': data
        }
        self.log_data['events'].append(event)
        
    def log_state(self, gesture: str, path: Any, terrain_type: str):
        """
        Log current vehicle state
        Args:
            gesture: Detected gesture
            path: Planned path waypoints
            terrain_type: Current classified terrain
        """
        self.log_event('state', {
            'gesture': gesture,
            'path': path,
            'terrain_type': terrain_type
        })
        
    def log_movement(self, direction: str, speed: float):
        """
        Log movement command
        Args:
            direction: Movement direction
            speed: Movement speed
        """
        self.log_event('movement', {
            'direction': direction,
            'speed': speed
        })
        
    def log_sensor_data(self, sensor_data: Dict[str, Any]):
        """
        Log sensor data
        Args:
            sensor_data: Sensor readings
        """
        self.log_event('sensor', sensor_data)
        
    def log_error(self, error_type: str, message: str):
        """
        Log error event
        Args:
            error_type: Type of error
            message: Error message
        """
        self.log_event('error', {
            'type': error_type,
            'message': message
        })
        
    def save_log(self):
        """
        Save current log data to file
        """
        self.log_data['end_time'] = time.time()
        self.log_data['duration'] = self.log_data['end_time'] - self.log_data['start_time']
        
        with open(self.log_file, 'w') as f:
            json.dump(self.log_data, f, indent=2)
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate statistics from logged data
        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_events': len(self.log_data['events']),
            'event_types': {},
            'duration': self.log_data.get('duration', 0)
        }
        
        # Count events by type
        for event in self.log_data['events']:
            event_type = event['type']
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
            
        return stats
        
    def __del__(self):
        """
        Save log data when object is destroyed
        """
        try:
            self.save_log()
        except Exception:
            pass 