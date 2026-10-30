import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any

class ControlPanel:
    def __init__(self, command_callback: Callable[[str, float], None]):
        """
        Initialize control panel
        Args:
            command_callback: Function to handle movement commands
        """
        self.root = tk.Tk()
        self.root.title("Car Control Panel")
        
        self.command_callback = command_callback
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create control elements
        self.create_direction_controls()
        self.create_speed_control()
        self.create_mode_controls()
        
        # Initialize state
        self.current_speed = tk.DoubleVar(value=0.0)
        self.current_mode = tk.StringVar(value="Manual")
        
    def create_direction_controls(self):
        """
        Create direction control buttons
        """
        direction_frame = ttk.LabelFrame(self.main_frame, text="Direction", padding="5")
        direction_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Direction buttons
        directions = {
            'FORWARD': (0, 1),
            'LEFT': (1, 0),
            'RIGHT': (1, 2),
            'BACKWARD': (2, 1),
            'STOP': (1, 1)
        }
        
        for direction, (row, col) in directions.items():
            btn = ttk.Button(
                direction_frame,
                text=direction,
                command=lambda d=direction: self.send_command(d)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            
    def create_speed_control(self):
        """
        Create speed control slider
        """
        speed_frame = ttk.LabelFrame(self.main_frame, text="Speed", padding="5")
        speed_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Speed slider
        self.speed_slider = ttk.Scale(
            speed_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.current_speed,
            command=self.update_speed
        )
        self.speed_slider.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Speed label
        self.speed_label = ttk.Label(speed_frame, text="0.0")
        self.speed_label.grid(row=0, column=1, padx=5)
        
    def create_mode_controls(self):
        """
        Create mode control buttons
        """
        mode_frame = ttk.LabelFrame(self.main_frame, text="Mode", padding="5")
        mode_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Mode buttons
        modes = ["Manual", "Autonomous", "Emergency Stop"]
        
        for i, mode in enumerate(modes):
            btn = ttk.Button(
                mode_frame,
                text=mode,
                command=lambda m=mode: self.set_mode(m)
            )
            btn.grid(row=0, column=i, padx=2, pady=2)
            
    def send_command(self, direction: str):
        """
        Send movement command
        Args:
            direction: Movement direction
        """
        if self.current_mode.get() == "Manual":
            self.command_callback(direction, self.current_speed.get())
            
    def update_speed(self, *args):
        """
        Update speed display and send command
        """
        speed = self.current_speed.get()
        self.speed_label.configure(text=f"{speed:.1f}")
        
        if self.current_mode.get() == "Manual":
            self.command_callback("FORWARD", speed)
            
    def set_mode(self, mode: str):
        """
        Set operation mode
        Args:
            mode: Operation mode
        """
        self.current_mode.set(mode)
        
        if mode == "Emergency Stop":
            self.command_callback("STOP", 0.0)
            self.current_speed.set(0.0)
            self.speed_slider.state(['disabled'])
        else:
            self.speed_slider.state(['!disabled'])
            
    def update_status(self, status: Dict[str, Any]):
        """
        Update control panel status
        Args:
            status: Status dictionary
        """
        # Update mode if provided
        if 'mode' in status:
            self.current_mode.set(status['mode'])
            
        # Update speed if provided
        if 'speed' in status:
            self.current_speed.set(status['speed'])
            
    def run(self):
        """
        Start control panel main loop
        """
        self.root.mainloop()
        
    def __del__(self):
        """
        Clean up resources
        """
        if hasattr(self, 'root'):
            self.root.destroy() 