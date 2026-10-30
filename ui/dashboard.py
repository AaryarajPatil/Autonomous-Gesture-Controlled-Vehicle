import cv2
import numpy as np
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging

logger = logging.getLogger(__name__)

class Dashboard:
    def __init__(self):
        """
        Initialize autonomous vehicle dashboard GUI.
        """
        self.root = tk.Tk()
        self.root.title("Autonomous Car Dashboard")
        self.is_running = True
        self._draw_counter = 0
        self._distance_traveled = 0.0
        self._battery_level = 100.0
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create video display
        self.video_label = ttk.Label(self.main_frame)
        self.video_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        # Create status indicators
        self.create_status_frame()
        
        # Create sensor data plot
        self.create_sensor_plot()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Initialize data storage
        self.sensor_data = {
            'speed': [0.0],
            'battery': [100.0],
            'distance': [0.0]
        }
        
    def create_status_frame(self):
        """
        Create status indicators frame
        """
        status_frame = ttk.LabelFrame(self.main_frame, text="Telemetry & System Status", padding="8")
        status_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status labels
        self.status_labels = {}
        status_items = [
            ('Mode', 'Autonomous'),
            ('Gesture', 'STOP'),
            ('Terrain', 'flat'),
            ('Speed', '0.0 m/s'),
            ('Battery', '100%'),
            ('Distance', '0.0 m')
        ]
        
        for i, (label, value) in enumerate(status_items):
            ttk.Label(status_frame, text=f"{label}:", font=('Helvetica', 9, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2)
            lbl = ttk.Label(status_frame, text=value, font=('Helvetica', 9))
            lbl.grid(row=i, column=1, sticky=tk.W, padx=10, pady=2)
            self.status_labels[label] = lbl
            
    def create_sensor_plot(self):
        """
        Create matplotlib sensor data plot
        """
        plot_frame = ttk.LabelFrame(self.main_frame, text="Real-Time Telemetry Plot", padding="5")
        plot_frame.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(4.5, 2.8), dpi=100)
        self.fig.tight_layout(pad=2.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E))
        
    def create_control_buttons(self):
        """
        Create control buttons
        """
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=8)
        
        # Control buttons
        ttk.Button(control_frame, text="▶ Start Autonomous", command=self.start).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="⏸ Manual Mode", command=self.stop).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="🔄 Reset System", command=self.reset).grid(row=0, column=2, padx=5)
        
    def update_video(self, frame: np.ndarray):
        """
        Update video display
        Args:
            frame: Input frame (BGR)
        """
        if not self.is_active() or frame is None:
            return
            
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (640, 360))
            ppm_data = cv2.imencode('.ppm', frame_resized)[1].tobytes()
            image = tk.PhotoImage(data=ppm_data)
            self.video_label.configure(image=image)
            self.video_label.image = image
        except Exception as e:
            logger.debug("Error updating video frame: %s", e)
            
    def update_status(self, status_or_gesture: Any = None, path: Any = None, terrain_type: Any = None):
        """
        Update status indicators and plot telemetry.
        Supports both dict input and positional arguments (gesture, path, terrain_type).
        """
        if not self.is_active():
            return
            
        if isinstance(status_or_gesture, dict):
            status = status_or_gesture
        else:
            gesture = str(status_or_gesture) if status_or_gesture is not None else "STOP"
            terrain_str = str(terrain_type) if terrain_type is not None else "flat"
            
            # Estimate speed based on gesture
            if gesture == "STOP":
                speed_num = 0.0
            elif gesture in ("LEFT", "RIGHT"):
                speed_num = 0.5
            elif gesture == "BACKWARD":
                speed_num = 0.3
            else:
                speed_num = 1.0
                
            self._distance_traveled += speed_num * 0.03
            self._battery_level = max(0.0, self._battery_level - 0.001)
            
            status = {
                'Gesture': gesture,
                'Terrain': terrain_str,
                'Speed': f"{speed_num:.2f} m/s",
                'Distance': f"{self._distance_traveled:.2f} m",
                'Battery': f"{self._battery_level:.1f}%"
            }
            
            self.update_sensor_data({
                'speed': speed_num,
                'battery': self._battery_level / 100.0,
                'distance': self._distance_traveled
            })
            
        for key, value in status.items():
            if key in self.status_labels:
                try:
                    self.status_labels[key].configure(text=str(value))
                except Exception:
                    pass
                    
    def update_sensor_data(self, data: Dict[str, float]):
        """
        Update sensor data plot (throttled for high frame rate performance)
        Args:
            data: Sensor data dictionary
        """
        for key, value in data.items():
            if key in self.sensor_data:
                self.sensor_data[key].append(value)
                if len(self.sensor_data[key]) > 60:
                    self.sensor_data[key].pop(0)
                    
        self._draw_counter += 1
        # Redraw every 5 updates (~6 FPS redraw) to keep Tkinter fast and responsive
        if self._draw_counter % 5 == 0 and self.is_active():
            try:
                self.ax.clear()
                for key, values in self.sensor_data.items():
                    self.ax.plot(values, label=key, linewidth=1.5)
                    
                self.ax.set_title("Telemetry History", fontsize=9)
                self.ax.set_xlabel("Recent Frames", fontsize=8)
                self.ax.set_ylabel("Normalized Value", fontsize=8)
                self.ax.legend(loc="upper right", fontsize=7)
                self.ax.grid(True, linestyle='--', alpha=0.6)
                self.canvas.draw_idle()
            except Exception as e:
                logger.debug("Error drawing plot: %s", e)
                
    def update_gui(self) -> bool:
        """
        Process pending Tkinter events.
        Returns:
            bool: True if dashboard is active, False if closed.
        """
        if not self.is_active():
            return False
        try:
            self.root.update_idletasks()
            self.root.update()
            return True
        except Exception:
            self.is_running = False
            return False
            
    def is_active(self) -> bool:
        """Check if dashboard GUI is open and running."""
        return self.is_running and (self.root is not None)
        
    def start(self):
        """Start autonomous operation"""
        if 'Mode' in self.status_labels:
            self.status_labels['Mode'].configure(text="Autonomous")
            
    def stop(self):
        """Stop autonomous operation"""
        if 'Mode' in self.status_labels:
            self.status_labels['Mode'].configure(text="Manual")
            
    def reset(self):
        """Reset dashboard data"""
        self._distance_traveled = 0.0
        self._battery_level = 100.0
        for key in self.sensor_data:
            self.sensor_data[key] = [0.0]
        self.update_status({
            'Mode': 'Autonomous',
            'Gesture': 'STOP',
            'Terrain': 'flat',
            'Speed': '0.0 m/s',
            'Battery': '100%',
            'Distance': '0.0 m'
        })
        
    def on_close(self):
        """Handle window close event gracefully."""
        self.is_running = False
        try:
            if self.root:
                self.root.destroy()
        except Exception:
            pass
        self.root = None
        
    def run(self):
        """Run dashboard main loop directly (if not running custom loop)."""
        if self.is_active():
            self.root.mainloop()
            
    def __del__(self):
        self.on_close()
