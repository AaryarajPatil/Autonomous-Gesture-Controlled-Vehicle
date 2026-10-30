import numpy as np
from typing import List, Tuple

class ObstacleAvoidance:
    def __init__(self):
        """
        Initialize obstacle avoidance system
        """
        self.safety_distance = 1.0  # meters
        self.max_speed = 1.0  # meters/second
        
    def avoid_obstacles(self, current_pos: Tuple[float, float],
                       target_pos: Tuple[float, float],
                       obstacles: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Calculate avoidance maneuver
        Args:
            current_pos: Current position
            target_pos: Target position
            obstacles: List of obstacle positions
        Returns:
            Adjusted target position
        """
        # Check if path to target is clear
        if self._is_path_clear(current_pos, target_pos, obstacles):
            return target_pos
            
        # Find safest alternative path
        return self._find_safe_path(current_pos, target_pos, obstacles)
        
    def _is_path_clear(self, start: Tuple[float, float],
                      end: Tuple[float, float],
                      obstacles: List[Tuple[float, float]]) -> bool:
        """
        Check if path between start and end is clear of obstacles
        Args:
            start: Start position
            end: End position
            obstacles: List of obstacle positions
        Returns:
            True if path is clear
        """
        # Check multiple points along the path
        num_points = 10
        for i in range(num_points + 1):
            t = i / num_points
            point = (
                start[0] + t * (end[0] - start[0]),
                start[1] + t * (end[1] - start[1])
            )
            
            # Check distance to all obstacles
            for obstacle in obstacles:
                distance = np.sqrt(
                    (point[0] - obstacle[0])**2 +
                    (point[1] - obstacle[1])**2
                )
                if distance < self.safety_distance:
                    return False
                    
        return True
        
    def _find_safe_path(self, start: Tuple[float, float],
                       target: Tuple[float, float],
                       obstacles: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Find a safe path around obstacles
        Args:
            start: Start position
            target: Target position
            obstacles: List of obstacle positions
        Returns:
            Safe target position
        """
        # Calculate direction to target
        direction = np.array([
            target[0] - start[0],
            target[1] - start[1]
        ])
        direction = direction / np.linalg.norm(direction)
        
        # Try different angles
        best_angle = 0
        max_distance = 0
        
        for angle in range(0, 360, 45):
            # Rotate direction vector
            theta = np.radians(angle)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array([[c, -s], [s, c]])
            rotated_direction = R.dot(direction)
            
            # Calculate new target
            new_target = (
                start[0] + rotated_direction[0] * self.max_speed,
                start[1] + rotated_direction[1] * self.max_speed
            )
            
            # Check if this path is safe
            if self._is_path_clear(start, new_target, obstacles):
                # Calculate distance to original target
                distance = np.sqrt(
                    (new_target[0] - target[0])**2 +
                    (new_target[1] - target[1])**2
                )
                
                if distance > max_distance:
                    max_distance = distance
                    best_angle = angle
                    
        if max_distance > 0:
            # Calculate best target position
            theta = np.radians(best_angle)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array([[c, -s], [s, c]])
            rotated_direction = R.dot(direction)
            return (
                start[0] + rotated_direction[0] * self.max_speed,
                start[1] + rotated_direction[1] * self.max_speed
            )
            
        # If no safe path found, return current position
        return start 