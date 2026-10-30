import numpy as np
from typing import Tuple, List
from dataclasses import dataclass

@dataclass
class Pose:
    x: float
    y: float
    theta: float  # heading in radians

class Localizer:
    def __init__(self):
        """
        Initialize localizer with initial pose
        """
        self.pose = Pose(0.0, 0.0, 0.0)
        self.velocity = 0.0
        self.angular_velocity = 0.0
        self.last_time = None
        
    def update(self, velocity: float, angular_velocity: float, timestamp: float):
        """
        Update position estimate using odometry
        Args:
            velocity: Linear velocity in m/s
            angular_velocity: Angular velocity in rad/s
            timestamp: Current timestamp in seconds
        """
        if self.last_time is None:
            self.last_time = timestamp
            return
            
        # Calculate time step
        dt = timestamp - self.last_time
        self.last_time = timestamp
        
        # Update velocities
        self.velocity = velocity
        self.angular_velocity = angular_velocity
        
        # Update pose using motion model
        if abs(angular_velocity) < 1e-6:
            # Straight line motion
            self.pose.x += velocity * np.cos(self.pose.theta) * dt
            self.pose.y += velocity * np.sin(self.pose.theta) * dt
        else:
            # Circular motion
            radius = velocity / angular_velocity
            self.pose.x += radius * (np.sin(self.pose.theta + angular_velocity * dt) -
                                   np.sin(self.pose.theta))
            self.pose.y += radius * (-np.cos(self.pose.theta + angular_velocity * dt) +
                                   np.cos(self.pose.theta))
            self.pose.theta += angular_velocity * dt
            
        # Normalize heading to [-pi, pi]
        self.pose.theta = np.arctan2(np.sin(self.pose.theta), np.cos(self.pose.theta))
        
    def get_pose(self) -> Pose:
        """
        Get current pose estimate
        Returns:
            Current pose
        """
        return self.pose
        
    def reset(self, pose: Pose = None):
        """
        Reset localizer to initial pose
        Args:
            pose: New pose to set (if None, reset to origin)
        """
        if pose is None:
            self.pose = Pose(0.0, 0.0, 0.0)
        else:
            self.pose = pose
        self.velocity = 0.0
        self.angular_velocity = 0.0
        self.last_time = None
        
    def predict_pose(self, time_delta: float) -> Pose:
        """
        Predict future pose
        Args:
            time_delta: Time to predict ahead in seconds
        Returns:
            Predicted pose
        """
        if abs(self.angular_velocity) < 1e-6:
            # Straight line prediction
            predicted_x = self.pose.x + self.velocity * np.cos(self.pose.theta) * time_delta
            predicted_y = self.pose.y + self.velocity * np.sin(self.pose.theta) * time_delta
            predicted_theta = self.pose.theta
        else:
            # Circular motion prediction
            radius = self.velocity / self.angular_velocity
            predicted_x = self.pose.x + radius * (np.sin(self.pose.theta + self.angular_velocity * time_delta) -
                                                np.sin(self.pose.theta))
            predicted_y = self.pose.y + radius * (-np.cos(self.pose.theta + self.angular_velocity * time_delta) +
                                                np.cos(self.pose.theta))
            predicted_theta = self.pose.theta + self.angular_velocity * time_delta
            
        return Pose(predicted_x, predicted_y, predicted_theta) 