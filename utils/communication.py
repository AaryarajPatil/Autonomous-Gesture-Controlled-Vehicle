import serial
import time
from typing import Optional, Dict, Any
import json

class ArduinoCommunication:
    def __init__(self, port: str = 'COM3', baud_rate: int = 9600, timeout: float = 1.0):
        """
        Initialize Arduino communication
        Args:
            port: Serial port name
            baud_rate: Communication speed
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to Arduino
        Returns:
            True if connection successful
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            return False
            
    def disconnect(self):
        """
        Disconnect from Arduino
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
        
    def send_command(self, command: str) -> bool:
        """
        Send command to Arduino
        Args:
            command: Command string to send
        Returns:
            True if command sent successfully
        """
        if not self.connected:
            return False
            
        try:
            self.serial.write(f"{command}\n".encode())
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
            
    def read_response(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Read response from Arduino
        Args:
            timeout: Optional timeout in seconds
        Returns:
            Response string or None if timeout
        """
        if not self.connected:
            return None
            
        try:
            if timeout:
                self.serial.timeout = timeout
            response = self.serial.readline().decode().strip()
            return response if response else None
        except Exception as e:
            print(f"Error reading response: {e}")
            return None
            
    def send_control_command(self, direction: str, speed: float) -> bool:
        """
        Send control command to Arduino
        Args:
            direction: Direction command (FORWARD, BACKWARD, LEFT, RIGHT, STOP)
            speed: Speed value (0.0 to 1.0)
        Returns:
            True if command sent successfully
        """
        command = f"CONTROL:{direction}:{speed:.2f}"
        return self.send_command(command)
        
    def send_sensor_request(self) -> Optional[Dict[str, Any]]:
        """
        Request sensor data from Arduino
        Returns:
            Dictionary of sensor data or None if request failed
        """
        if not self.send_command("SENSOR_REQUEST"):
            return None
            
        response = self.read_response()
        if not response:
            return None
            
        try:
            # Parse sensor data from response
            # Format: "SENSOR_DATA:distance:temperature:humidity"
            parts = response.split(':')
            if len(parts) != 4 or parts[0] != "SENSOR_DATA":
                return None
                
            return {
                'distance': float(parts[1]),
                'temperature': float(parts[2]),
                'humidity': float(parts[3])
            }
        except Exception as e:
            print(f"Error parsing sensor data: {e}")
            return None
            
    def send_emergency_stop(self) -> bool:
        """
        Send emergency stop command
        Returns:
            True if command sent successfully
        """
        return self.send_command("EMERGENCY_STOP")
        
    def send_reset(self) -> bool:
        """
        Send reset command
        Returns:
            True if command sent successfully
        """
        return self.send_command("RESET")
        
    def is_connected(self) -> bool:
        """
        Check if connected to Arduino
        Returns:
            True if connected
        """
        return self.connected
        
    def send_movement_command(self, direction: str, speed: float):
        """
        Send movement command to Arduino
        Args:
            direction: Movement direction
            speed: Movement speed (0-1)
        """
        command = {
            'type': 'MOVE',
            'direction': direction,
            'speed': speed
        }
        self.send_command(json.dumps(command))
        
    def send_stop_command(self):
        """
        Send stop command to Arduino
        """
        command = {
            'type': 'STOP'
        }
        self.send_command(json.dumps(command))
        
    def get_sensor_data(self) -> Dict[str, Any]:
        """
        Request and read sensor data from Arduino
        Returns:
            Sensor data dictionary
        """
        command = {
            'type': 'SENSORS'
        }
        self.send_command(json.dumps(command))
        return self.read_response()
        
    def __del__(self):
        self.disconnect() 