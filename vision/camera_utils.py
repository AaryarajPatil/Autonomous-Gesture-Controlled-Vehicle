import cv2
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, camera_id=0, width=640, height=480, fps=30, mock_fallback=True):
        """
        Initialize camera
        Args:
            camera_id (int): Camera device ID (default: 0 for primary camera)
            width (int): Frame width
            height (int): Frame height
            fps (int): Frame rate
            mock_fallback (bool): If True, falls back to simulated feed if camera fails
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.mock_fallback = mock_fallback
        self.is_mock = False
        self.camera = None
        self._frame_count = 0
        self._start_time = time.time()
        
        try:
            self.camera = cv2.VideoCapture(camera_id)
            if not self.camera.isOpened():
                if self.mock_fallback:
                    logger.warning("No physical camera detected at device %d. Enabling mock camera feed.", camera_id)
                    self.is_mock = True
                    if self.camera is not None:
                        self.camera.release()
                    self.camera = None
                else:
                    raise RuntimeError("Failed to open camera")
            else:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        except Exception as e:
            if self.mock_fallback:
                logger.warning("Camera init failed (%s). Falling back to mock feed.", e)
                self.is_mock = True
                self.camera = None
            else:
                raise
                
    def get_frame(self):
        """
        Capture and return a frame from the camera
        Returns:
            numpy.ndarray: Captured frame (BGR) or None
        """
        if self.is_mock or self.camera is None:
            return self._generate_mock_frame()
            
        ret, frame = self.camera.read()
        if not ret or frame is None:
            if self.mock_fallback:
                return self._generate_mock_frame()
            return None
            
        return frame
        
    def _generate_mock_frame(self) -> np.ndarray:
        """
        Generate a synthetic video frame simulating a forward vehicle view with road & gesture guidance.
        """
        self._frame_count += 1
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # 1. Sky / Upper horizon (Dark navy gradient)
        horizon_y = int(self.height * 0.42)
        frame[0:horizon_y, :] = [45, 30, 20]
        
        # 2. Road surface (Dark gray asphalt)
        frame[horizon_y:, :] = [50, 50, 50]
        
        # 3. Perspective road boundaries (green grass on sides)
        left_top = (int(self.width * 0.38), horizon_y)
        left_bottom = (0, self.height)
        right_top = (int(self.width * 0.62), horizon_y)
        right_bottom = (self.width, self.height)
        
        left_grass = np.array([[0, horizon_y], left_top, left_bottom, [0, self.height]], np.int32)
        right_grass = np.array([right_top, [self.width, horizon_y], [self.width, self.height], right_bottom], np.int32)
        cv2.fillPoly(frame, [left_grass], [25, 60, 25])
        cv2.fillPoly(frame, [right_grass], [25, 60, 25])
        
        # 4. Road borders (white lines)
        cv2.line(frame, left_top, left_bottom, (220, 220, 220), 3)
        cv2.line(frame, right_top, right_bottom, (220, 220, 220), 3)
        
        # 5. Animated dashed center lane marking
        offset = (self._frame_count * 8) % 60
        center_top = (int(self.width * 0.50), horizon_y)
        center_bottom = (int(self.width * 0.50), self.height)
        
        total_road_h = self.height - horizon_y
        for y_rel in range(-60 + offset, total_road_h, 60):
            y_start = horizon_y + y_rel
            y_end = y_start + 30
            if y_end > horizon_y and y_start < self.height:
                ys = max(horizon_y, y_start)
                ye = min(self.height, y_end)
                cv2.line(frame, (center_top[0], ys), (center_bottom[0], ye), (0, 215, 255), 4)
                
        # 6. Car bonnet/hood at bottom
        hood_pts = np.array([
            [int(self.width * 0.25), self.height],
            [int(self.width * 0.35), self.height - 40],
            [int(self.width * 0.65), self.height - 40],
            [int(self.width * 0.75), self.height]
        ], np.int32)
        cv2.fillPoly(frame, [hood_pts], [35, 35, 120])
        cv2.polylines(frame, [hood_pts], False, (0, 165, 255), 2)
        
        # 7. Simulated Gesture Hand Inset in top-right corner
        inset_w, inset_h = 160, 120
        ix, iy = self.width - inset_w - 15, 15
        cv2.rectangle(frame, (ix, iy), (ix + inset_w, iy + inset_h), (30, 30, 30), -1)
        cv2.rectangle(frame, (ix, iy), (ix + inset_w, iy + inset_h), (0, 255, 0), 2)
        cv2.putText(frame, "SIMULATED SENSOR", (ix + 10, iy + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Draw palm / hand representation
        center_hand = (ix + inset_w // 2, iy + inset_h // 2 + 10)
        cv2.circle(frame, center_hand, 22, (200, 180, 160), -1)
        # Fingers
        for angle_deg in [-50, -25, 0, 25, 50]:
            rad = np.radians(angle_deg - 90)
            fx = int(center_hand[0] + 38 * np.cos(rad))
            fy = int(center_hand[1] + 38 * np.sin(rad))
            cv2.line(frame, center_hand, (fx, fy), (200, 180, 160), 6)
            cv2.circle(frame, (fx, fy), 5, (0, 255, 255), -1)
        
        # 8. Feed Info text
        elapsed = time.time() - self._start_time
        cv2.putText(frame, "FEED: SIMULATION MODE (VIRTUAL CAR)", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, f"FPS: ~{self.fps} | Frame: {self._frame_count} | Uptime: {elapsed:.1f}s", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
        
    def release(self):
        """Release the camera"""
        if self.camera is not None:
            try:
                self.camera.release()
            except Exception:
                pass
            self.camera = None
            
    def __del__(self):
        self.release()
