import cv2
import numpy as np
import logging
import time
from .camera_utils import Camera

logger = logging.getLogger(__name__)

class GestureRecognizer:
    def __init__(self, camera: Camera = None):
        """
        Initialize Gesture Recognizer with MediaPipe or OpenCV computer-vision fallback.
        """
        self.camera = camera if camera is not None else Camera()
        self.current_frame = None
        self._frame_count = 0
        self._last_gesture = "STOP"
        
        # Check for legacy MediaPipe solutions
        self.has_mp_solutions = False
        try:
            import mediapipe as mp
            if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands'):
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
                self.mp_draw = mp.solutions.drawing_utils
                self.has_mp_solutions = True
                logger.info("MediaPipe hands solutions loaded successfully.")
            else:
                logger.info("MediaPipe solutions not present in current build. Using OpenCV / Simulation gesture processor.")
        except Exception as e:
            logger.warning("Could not initialize MediaPipe hands (%s). Using OpenCV fallback.", e)
            
    def get_current_frame(self):
        """Return the most recently processed frame with visual annotations."""
        return self.current_frame
        
    def detect_gesture(self) -> str:
        """
        Detect and classify hand gestures from camera feed
        Returns:
            str: Detected gesture ('FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'STOP')
        """
        frame = self.camera.get_frame()
        if frame is None:
            self._last_gesture = "STOP"
            return "STOP"
            
        annotated_frame = frame.copy()
        gesture = "STOP"
        self._frame_count += 1
        
        # 1. MediaPipe Solutions Path (if installed and available)
        if self.has_mp_solutions:
            try:
                rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    self.mp_draw.draw_landmarks(
                        annotated_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    gesture = self._classify_gesture(hand_landmarks)
                else:
                    gesture = "STOP"
            except Exception as e:
                logger.debug("MediaPipe process error: %s", e)
                gesture = "STOP"
                
        # 2. Simulated / Camera-based fallback
        else:
            if getattr(self.camera, 'is_mock', False):
                # In simulation mode, generate a realistic autonomous vehicle demonstration sequence
                # (Forward -> Left turn -> Forward -> Right turn -> Stop)
                cycle_step = (self._frame_count // 45) % 8
                sequence = [
                    "FORWARD", "FORWARD", "LEFT",
                    "FORWARD", "FORWARD", "RIGHT",
                    "FORWARD", "STOP"
                ]
                gesture = sequence[cycle_step]
                
                # Visual overlay on simulated camera feed
                h, w = annotated_frame.shape[:2]
                box_color = (0, 255, 0) if gesture != "STOP" else (0, 0, 255)
                cv2.rectangle(annotated_frame, (15, h - 90), (320, h - 15), (20, 20, 20), -1)
                cv2.rectangle(annotated_frame, (15, h - 90), (320, h - 15), box_color, 2)
                cv2.putText(annotated_frame, f"RECOGNIZED: {gesture}", (25, h - 45),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, box_color, 2)
            else:
                # Real webcam OpenCV skin detection & contour analysis
                gesture = self._detect_gesture_opencv(annotated_frame)
                
        self.current_frame = annotated_frame
        self._last_gesture = gesture
        return gesture

    def _detect_gesture_opencv(self, frame: np.ndarray) -> str:
        """
        OpenCV skin-color thresholding & contour hull analysis when MediaPipe solutions is unavailable.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Skin color range in HSV
        lower_skin = np.array([0, 30, 60], dtype=np.uint8)
        upper_skin = np.array([20, 150, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Morphological filtering to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return "STOP"
            
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)
        if area < 5000:
            return "STOP"
            
        # Draw bounding rect and contour
        cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)
        hull = cv2.convexHull(max_contour, returnPoints=False)
        if hull is None or len(hull) <= 3:
            return "STOP"
            
        try:
            defects = cv2.convexityDefects(max_contour, hull)
            if defects is None:
                return "STOP"
                
            finger_count = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(max_contour[s][0])
                end = tuple(max_contour[e][0])
                far = tuple(max_contour[f][0])
                
                # Triangle side lengths
                a = np.linalg.norm(np.array(end) - np.array(start))
                b = np.linalg.norm(np.array(far) - np.array(start))
                c = np.linalg.norm(np.array(end) - np.array(far))
                # Cosine rule for angle
                angle = np.arccos(np.clip((b**2 + c**2 - a**2) / (2 * b * c + 1e-6), -1.0, 1.0))
                if angle <= np.pi / 2 and d > 10000:
                    finger_count += 1
                    cv2.circle(frame, far, 4, [0, 0, 255], -1)
                    
            if finger_count >= 3:
                return "FORWARD"
            elif finger_count == 2:
                return "LEFT"
            elif finger_count == 1:
                return "RIGHT"
            else:
                return "STOP"
        except Exception:
            return "STOP"
        
    def _classify_gesture(self, landmarks):
        """
        Classify gesture based on MediaPipe hand landmark positions
        """
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        wrist = landmarks.landmark[0]
        
        # Check finger extensions
        index_open = index_tip.y < wrist.y
        middle_open = middle_tip.y < wrist.y
        ring_open = ring_tip.y < wrist.y
        pinky_open = pinky_tip.y < wrist.y
        
        open_fingers = sum([index_open, middle_open, ring_open, pinky_open])
        
        if open_fingers >= 4:
            return "FORWARD"
        elif index_open and not middle_open and not ring_open:
            if index_tip.x < wrist.x - 0.1:
                return "LEFT"
            elif index_tip.x > wrist.x + 0.1:
                return "RIGHT"
            return "FORWARD"
        elif open_fingers == 0:
            return "STOP"
        else:
            return "STOP"
            
    def release(self):
        """Release underlying camera"""
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()
            
    def __del__(self):
        self.release()
