import numpy as np
from typing import List, Tuple, Dict
import json

class EnvironmentMapper:
    def __init__(self, map_size: Tuple[int, int] = (100, 100), resolution: float = 0.1):
        """
        Initialize environment mapper
        Args:
            map_size: Size of the map in cells (width, height)
            resolution: Map resolution in meters per cell
        """
        self.map_size = map_size
        self.resolution = resolution
        self.grid_map = np.zeros(map_size, dtype=np.int8)
        self.obstacles = []
        self.visited_positions = set()
        
    def update_map(self, position: Tuple[float, float],
                  obstacles: List[Tuple[float, float]]):
        """
        Update the environment map with new sensor data
        Args:
            position: Current position
            obstacles: List of detected obstacle positions
        """
        # Convert position to grid coordinates
        grid_pos = self._world_to_grid(position)
        
        # Mark current position as visited
        self.visited_positions.add(grid_pos)
        
        # Update obstacles
        self.obstacles = obstacles
        for obstacle in obstacles:
            grid_obstacle = self._world_to_grid(obstacle)
            if self._is_valid_grid_pos(grid_obstacle):
                self.grid_map[grid_obstacle] = 1
                
    def get_map(self) -> np.ndarray:
        """
        Get the current environment map
        Returns:
            numpy.ndarray: Grid map with obstacles and visited positions
        """
        map_copy = self.grid_map.copy()
        
        # Mark visited positions
        for pos in self.visited_positions:
            if self._is_valid_grid_pos(pos):
                map_copy[pos] = 2
                
        return map_copy
        
    def save_map(self, filename: str):
        """
        Save the environment map to a file
        Args:
            filename: Output file path
        """
        map_data = {
            'map_size': self.map_size,
            'resolution': self.resolution,
            'grid_map': self.grid_map.tolist(),
            'obstacles': self.obstacles,
            'visited_positions': list(self.visited_positions)
        }
        
        with open(filename, 'w') as f:
            json.dump(map_data, f)
            
    def load_map(self, filename: str):
        """
        Load the environment map from a file
        Args:
            filename: Input file path
        """
        with open(filename, 'r') as f:
            map_data = json.load(f)
            
        self.map_size = tuple(map_data['map_size'])
        self.resolution = map_data['resolution']
        self.grid_map = np.array(map_data['grid_map'])
        self.obstacles = map_data['obstacles']
        self.visited_positions = set(tuple(pos) for pos in map_data['visited_positions'])
        
    def _world_to_grid(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """
        Convert world coordinates to grid coordinates
        Args:
            position: World position (x, y) in meters
        Returns:
            Grid position (x, y) in cells
        """
        return (
            int(position[0] / self.resolution),
            int(position[1] / self.resolution)
        )
        
    def _grid_to_world(self, grid_pos: Tuple[int, int]) -> Tuple[float, float]:
        """
        Convert grid coordinates to world coordinates
        Args:
            grid_pos: Grid position (x, y) in cells
        Returns:
            World position (x, y) in meters
        """
        return (
            grid_pos[0] * self.resolution,
            grid_pos[1] * self.resolution
        )
        
    def _is_valid_grid_pos(self, grid_pos: Tuple[int, int]) -> bool:
        """
        Check if grid position is valid
        Args:
            grid_pos: Grid position to check
        Returns:
            True if position is valid
        """
        return (0 <= grid_pos[0] < self.map_size[0] and
                0 <= grid_pos[1] < self.map_size[1]) 