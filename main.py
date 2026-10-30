#!/usr/bin/env python3

import sys
import time
import logging
from utils.config import Config
from utils.data_logger import DataLogger
from vision.gesture_recognition import GestureRecognizer
from navigation.path_planning import PathPlanner
from terrain.terrain_classifier import TerrainClassifier
from ui.dashboard import Dashboard

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    logger.info("Starting Autonomous Gesture-Controlled Car")
    
    gesture_recognizer = None
    data_logger = None
    
    try:
        # Initialize components
        config = Config()
        data_logger = DataLogger()
        gesture_recognizer = GestureRecognizer()
        path_planner = PathPlanner()
        terrain_classifier = TerrainClassifier()
        dashboard = Dashboard()
        
        logger.info("All modules initialized. Entering real-time control loop.")
        
        last_log_time = 0.0
        last_gesture = None
        
        # Main control loop
        while True:
            # Process gesture input
            gesture = gesture_recognizer.detect_gesture()
            
            # Plan path based on gesture and environment
            path = path_planner.plan_path(gesture)
            
            # Classify terrain and adjust speed
            terrain_type = terrain_classifier.classify_terrain()
            
            # Update dashboard status and plot
            dashboard.update_status(gesture, path, terrain_type)
            
            # Update dashboard video feed with annotated visuals
            frame = gesture_recognizer.get_current_frame()
            if frame is not None:
                dashboard.update_video(frame)
                
            # Process Tkinter GUI events (returns False if user closed window)
            if not dashboard.update_gui():
                logger.info("Dashboard window closed by user. Exiting main loop.")
                break
            
            # Log data
            data_logger.log_state(gesture, path, terrain_type)
            
            # Periodic console output (every 2 seconds or on gesture change)
            now = time.time()
            if gesture != last_gesture or (now - last_log_time >= 2.0):
                logger.info(f"State: Gesture='{gesture}', Terrain='{terrain_type}', Waypoints={len(path)}")
                last_gesture = gesture
                last_log_time = now
                
            # Regulate frame rate to ~30 FPS
            time.sleep(0.03)
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Saving session logs and releasing resources...")
        if data_logger is not None:
            try:
                data_logger.save_log()
                logger.info("Log file saved successfully.")
            except Exception:
                pass
        if gesture_recognizer is not None:
            gesture_recognizer.release()
        logger.info("Autonomous Car system stopped.")

if __name__ == "__main__":
    main()
