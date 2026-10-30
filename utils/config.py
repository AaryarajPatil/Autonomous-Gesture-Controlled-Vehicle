import json
import os
from typing import Dict, Any

class Config:
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_default_config()
        
        # Load custom config if exists
        if os.path.exists(config_file):
            self._load_config()
            
    def _load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration
        Returns:
            Default configuration dictionary
        """
        return {
            'arduino': {
                'port': 'COM3',
                'baud_rate': 9600,
                'timeout': 1
            },
            'camera': {
                'device_id': 0,
                'width': 640,
                'height': 480,
                'fps': 30
            },
            'vision': {
                'gesture_detection': {
                    'min_detection_confidence': 0.7,
                    'min_tracking_confidence': 0.5
                },
                'object_detection': {
                    'confidence_threshold': 0.5,
                    'nms_threshold': 0.4
                }
            },
            'navigation': {
                'safety_distance': 1.0,
                'max_speed': 1.0,
                'map_resolution': 0.1,
                'map_size': [100, 100]
            },
            'terrain': {
                'speed_profiles': {
                    'flat': {'max_speed': 1.0, 'acceleration': 0.5, 'deceleration': 0.5},
                    'smooth': {'max_speed': 0.8, 'acceleration': 0.4, 'deceleration': 0.4},
                    'rough': {'max_speed': 0.5, 'acceleration': 0.3, 'deceleration': 0.3},
                    'steep': {'max_speed': 0.3, 'acceleration': 0.2, 'deceleration': 0.2}
                }
            },
            'logging': {
                'log_dir': 'logs',
                'log_level': 'INFO'
            }
        }
        
    def _load_config(self):
        """
        Load configuration from file
        """
        try:
            with open(self.config_file, 'r') as f:
                custom_config = json.load(f)
                self._update_config(self.config, custom_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def _update_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """
        Recursively update configuration dictionary
        Args:
            base: Base configuration dictionary
            update: Update configuration dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._update_config(base[key], value)
            else:
                base[key] = value
                
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
        Returns:
            Configuration value
        """
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any):
        """
        Set configuration value
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            config = config.setdefault(k, {})
            
        config[keys[-1]] = value
        
    def save(self):
        """
        Save current configuration to file
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def reset(self):
        """
        Reset configuration to defaults
        """
        self.config = self._load_default_config()
        self.save() 