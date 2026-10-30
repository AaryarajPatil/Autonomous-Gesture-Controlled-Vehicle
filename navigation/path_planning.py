import numpy as np
from typing import List, Tuple

class PathPlanner:
    def __init__(self):
        """
        Initialize path planner
        """
        self.current_path = []
        self.obstacles = []
        
    def plan_path(self, gesture: str, obstacles: List[Tuple[float, float]] = None) -> List[Tuple[float, float]]:
        """
        Plan a path based on gesture and obstacles
        Args:
            gesture: Detected hand gesture
            obstacles: List of obstacle positions
        Returns:
            List of waypoints forming the path
        """
        if obstacles:
            self.obstacles = obstacles
            
        # Convert gesture to movement direction
        direction = self._gesture_to_direction(gesture)
        
        # Generate path based on direction and obstacles
        path = self._generate_path(direction)
        
        self.current_path = path
        return path
        
    def _gesture_to_direction(self, gesture: str) -> Tuple[float, float]:
        """
        Convert gesture to movement direction vector
        Args:
            gesture: Detected hand gesture
        Returns:
            Direction vector (x, y)
        """
        directions = {
            "FORWARD": (0, 1),
            "BACKWARD": (0, -1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0),
            "STOP": (0, 0)
        }
        return directions.get(gesture, (0, 0))
        
    def _generate_path(self, direction: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Generate path considering obstacles
        Args:
            direction: Movement direction vector
        Returns:
            List of waypoints
        """
        # Simple path generation - can be enhanced with more sophisticated algorithms
        path = []
        current_pos = (0, 0)  # Starting position
        
        # Generate waypoints
        for _ in range(10):  # Generate 10 waypoints
            next_pos = (
                current_pos[0] + direction[0],
                current_pos[1] + direction[1]
            )
            
            # Check if next position collides with obstacles
            if not self._check_collision(next_pos):
                path.append(next_pos)
                current_pos = next_pos
            else:
                # Try to find alternative path around obstacle
                alternative = self._find_alternative_path(current_pos, direction)
                if alternative:
                    path.extend(alternative)
                    current_pos = alternative[-1]
                else:
                    break
                    
        return path
        
    def _check_collision(self, position: Tuple[float, float]) -> bool:
        """
        Check if position collides with obstacles
        Args:
            position: Position to check
        Returns:
            True if collision detected
        """
        for obstacle in self.obstacles:
            distance = np.sqrt(
                (position[0] - obstacle[0])**2 +
                (position[1] - obstacle[1])**2
            )
            if distance < 1.0:  # Collision threshold
                return True
        return False
        
    def _find_alternative_path(self, current_pos: Tuple[float, float],
                             direction: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Find alternative path around obstacle
        Args:
            current_pos: Current position
            direction: Original movement direction
        Returns:
            List of waypoints forming alternative path
        """
        # Simple alternative path generation - can be enhanced
        alternatives = []
        
        # Try perpendicular directions
        perpendicular = (-direction[1], direction[0])
        alt_pos = (
            current_pos[0] + perpendicular[0],
            current_pos[1] + perpendicular[1]
        )
        
        if not self._check_collision(alt_pos):
            alternatives.append(alt_pos)
            return alternatives
            
        return None 