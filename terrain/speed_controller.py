from typing import Dict
from dataclasses import dataclass

@dataclass
class SpeedProfile:
    max_speed: float
    acceleration: float
    deceleration: float

class SpeedController:
    def __init__(self):
        """
        Initialize speed controller
        """
        # Define speed profiles for different terrain types
        self.speed_profiles = {
            'flat': SpeedProfile(1.0, 0.5, 0.5),
            'smooth': SpeedProfile(0.8, 0.4, 0.4),
            'rough': SpeedProfile(0.5, 0.3, 0.3),
            'steep': SpeedProfile(0.3, 0.2, 0.2)
        }
        
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.current_profile = self.speed_profiles['flat']
        
    def update_speed(self, terrain_type: str, obstacle_distance: float = None) -> float:
        """
        Update speed based on terrain type and obstacles
        Args:
            terrain_type: Current terrain type
            obstacle_distance: Distance to nearest obstacle (if any)
        Returns:
            Updated speed
        """
        # Update speed profile based on terrain
        self.current_profile = self.speed_profiles[terrain_type]
        
        # Set target speed based on terrain
        self.target_speed = self.current_profile.max_speed
        
        # Adjust for obstacles if present
        if obstacle_distance is not None:
            self._adjust_for_obstacles(obstacle_distance)
            
        # Update current speed
        self._update_current_speed()
        
        return self.current_speed
        
    def _adjust_for_obstacles(self, distance: float):
        """
        Adjust target speed based on obstacle distance
        Args:
            distance: Distance to nearest obstacle
        """
        if distance < 1.0:  # Very close to obstacle
            self.target_speed = 0.0
        elif distance < 2.0:  # Close to obstacle
            self.target_speed *= 0.5
        elif distance < 3.0:  # Moderate distance
            self.target_speed *= 0.7
            
    def _update_current_speed(self):
        """
        Update current speed based on target speed and acceleration/deceleration
        """
        if self.current_speed < self.target_speed:
            # Accelerate
            self.current_speed = min(
                self.current_speed + self.current_profile.acceleration,
                self.target_speed
            )
        elif self.current_speed > self.target_speed:
            # Decelerate
            self.current_speed = max(
                self.current_speed - self.current_profile.deceleration,
                self.target_speed
            )
            
    def get_speed_profile(self, terrain_type: str) -> SpeedProfile:
        """
        Get speed profile for terrain type
        Args:
            terrain_type: Terrain type
        Returns:
            Speed profile for terrain
        """
        return self.speed_profiles.get(terrain_type, self.speed_profiles['flat'])
        
    def reset(self):
        """
        Reset speed controller to initial state
        """
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.current_profile = self.speed_profiles['flat'] 