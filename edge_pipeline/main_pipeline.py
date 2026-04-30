#!/usr/bin/env python3
"""
Edge Main Pipeline - Raspberry Pi 5 Optimized
Real-time traffic violation detection with USB webcam
"""

import cv2
import threading
import queue
import time
import logging
import numpy as np
from pathlib import Path
from collections import deque
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FrameData:
    """Frame data passed through pipeline"""
    frame_id: int
    timestamp: float
    frame: np.ndarray


@dataclass
class InferenceResult:
    """Inference result"""
    frame_id: int
    timestamp: float
    frame: np.ndarray
    detections: list
    violations: list


class EdgePipeline:
    """Main pipeline for edge deployment"""
    
    def __init__(self, camera_source: int = 0, show_display: bool = False):
        logger.info("Initializing EdgePipeline")
        
        self.camera_source = camera_source
        self.show_display = show_display
        
        # Queues
        self.capture_queue = queue.Queue(maxsize=2)
        self.infer_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue(maxsize=4)
        
        self.stop_event = threading.Event()
        self.threads = []
        
        # Components (lazy loaded)
        self.camera = None
        self.detector = None
        self.tracker = None
        self.violation_gate = None
        self.ocr = None
        self.gps_reader = None
        self.speed_detector = None
        
        # Statistics
        self.stats = {
            'start_time': None,
            'total_frames': 0,
            'violations_detected': 0,
            'plates_read': 0,
            'speed_violations': 0,
        }
        
        logger.info(f"EdgePipeline created | Camera: {camera_source} | Display: {show_display}")
    
    def start(self):
        """Start pipeline"""
        if self.stats['start_time'] is not None:
            logger.warning("Pipeline already started")
            return
        
        logger.info("Starting EdgePipeline")
        self.stats['start_time'] = time.time()
        
        self._init_components()
        self._print_startup_summary()
        
        # Start camera
        from edge_pipeline.camera_stream import EdgeCameraStream
        self.camera = EdgeCameraStream(
            source=self.camera_source,
            width=1280,
            height=720,
            fps=30
        )
        self.camera.start()
        logger.info("✓ Camera started")
        
        # Start inference thread
        inference_thread = threading.Thread(
            target=self._inference_thread,
            daemon=True,
            name="EdgeInferenceThread"
        )
        inference_thread.start()
        self.threads.append(inference_thread)
        logger.info("✓ Inference thread started")
        
        # Start logging thread
        log_thread = threading.Thread(
            target=self._log_thread,
            daemon=True,
            name="EdgeLogThread"
        )
        log_thread.start()
        self.threads.append(log_thread)
        logger.info("✓ Logging thread started")
        
        logger.info("All threads started. Running pipeline...")
        
        # Main loop
        if self.show_display:
            try:
                self._display_loop()
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
            finally:
                self.stop()
        else:
            # Headless mode - just keep running
            try:
                while not self.stop_event.is_set():
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
            finally:
                self.stop()
    
    def stop(self):
        """Stop pipeline"""
        logger.info("Stopping EdgePipeline")
        
        self.stop_event.set()
        time.sleep(2)
        
        if self.camera:
            self.camera.stop()
        
        if self.gps_reader:
            self.gps_reader.stop()
        
        self._print_session_summary()
        logger.info("Pipeline stopped")
    
    def _init_components(self):
        """Initialize components"""
        logger.info("Initializing components...")
        
        # Get settings
        from edge_config.settings import get_settings
        settings = get_settings()
        
        # Detector
        try:
            from edge_core.detector import Detector
            self.detector = Detector(
                model_path=settings.yolo_model_path,
                inference_size=settings.inference_size,
                num_threads=settings.num_threads,
                confidence_threshold=settings.detection_confidence,
            )
            logger.info("✓ Detector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Detector: {e}")
        
        # Tracker
        try:
            from edge_core.tracker import EdgeTracker
            self.tracker = EdgeTracker()
            logger.info("✓ Tracker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Tracker: {e}")
        
        # Violation Gate
        try:
            from edge_core.violation_gate import ViolationGate
            self.violation_gate = ViolationGate()
            logger.info("✓ Violation Gate initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Violation Gate: {e}")
        
        # OCR
        try:
            from edge_core.ocr import EdgeOCR
            self.ocr = EdgeOCR()
            logger.info("✓ OCR initialized")
        except Exception as e:
            logger.warning(f"OCR not available: {e}")
        
        # GPS
        try:
            from edge_core.gps_reader import EdgeGPSReader
            self.gps_reader = EdgeGPSReader()
            self.gps_reader.start()
            logger.info("✓ GPS Reader initialized")
        except Exception as e:
            logger.warning(f"GPS not available: {e}")
        
        # Storage Manager
        try:
            from edge_core.storage_manager import StorageManager
            self.storage_manager = StorageManager(max_storage_mb=8000)
            logger.info("✓ Storage Manager initialized")
            # Run initial cleanup check
            self.storage_manager.check_and_cleanup()
        except Exception as e:
            logger.warning(f"Storage Manager not available: {e}")
            self.storage_manager = None
        
        # Speed Detector
        try:
            from edge_core.speed_detector import SpeedDetector, SpeedConfig
            speed_config = SpeedConfig(
                pixels_per_meter=settings.pixels_per_meter if hasattr(settings, 'pixels_per_meter') else 8.0,
                fps=settings.camera_fps if hasattr(settings, 'camera_fps') else 30.0,
                speed_limit_kmh=settings.speed_limit_kmh if hasattr(settings, 'speed_limit_kmh') else 60.0,
                violation_threshold_kmh=settings.speed_violation_threshold if hasattr(settings, 'speed_violation_threshold') else 60.0,
            )
            self.speed_detector = SpeedDetector(config=speed_config)
            logger.info("✓ Speed Detector initialized")
        except Exception as e:
            logger.warning(f"Speed Detector not available: {e}")
            self.speed_detector = None
        
        logger.info("Component initialization complete")
    
    def _inference_thread(self):
        """Inference thread"""
        logger.info("Inference thread started")
        frame_id = 0
        
        while not self.stop_event.is_set():
            try:
                # Get frame from camera
                frame = self.camera.read() if self.camera else None
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                frame_id += 1
                timestamp = time.time()
                
                # Run detection
                detections = []
                violations = []
                speed_results = {}
                
                if self.detector and self.tracker and self.violation_gate:
                    detections = self.detector.infer(frame)
                    tracks = self.tracker.update(detections, frame)
                    violations = self.violation_gate.process(detections, tracks, frame_id)
                    
                    # Speed detection
                    if self.speed_detector and tracks:
                        speed_results = self.speed_detector.process_tracks(
                            tracks, frame_id, timestamp
                        )
                        
                        # Add speed violations to violations list
                        for track_id, speed_data in speed_results.items():
                            if speed_data['is_violation']:
                                # Find corresponding track
                                track = next((t for t in tracks if t.track_id == track_id), None)
                                if track:
                                    violations.append({
                                        'violation_type': 'overspeed',
                                        'track_id': track_id,
                                        'speed_kmh': speed_data['speed_kmh'],
                                        'speed_limit': speed_data['speed_limit'],
                                        'bbox': (track.x1, track.y1, track.x2, track.y2),
                                        'position': speed_data['position'],
                                    })
                                    self.stats['speed_violations'] += 1
                        
                        # Draw speed overlay on frame
                        for track_id, speed_data in speed_results.items():
                            from edge_core.speed_detector import draw_speed_overlay
                            draw_speed_overlay(
                                frame,
                                track_id,
                                speed_data['position'],
                                speed_data['speed_kmh'],
                                speed_data['is_violation']
                            )
                    
                    self.stats['violations_detected'] += len(violations)
                
                # Create result
                result = InferenceResult(
                    frame_id=frame_id,
                    timestamp=timestamp,
                    frame=frame,
                    detections=detections,
                    violations=violations
                )
                
                # Push to result queue
                try:
                    self.result_queue.put(result, timeout=0.1)
                except queue.Full:
                    pass
                
                self.stats['total_frames'] += 1
            
            except Exception as e:
                logger.error(f"Inference thread error: {e}")
        
        logger.info("Inference thread stopped")
    
    def _log_thread(self):
        """Logging thread"""
        logger.info("Logging thread started")
        
        cleanup_counter = 0
        
        while not self.stop_event.is_set():
            try:
                result = self.result_queue.get(timeout=0.5)
                
                for violation in result.violations:
                    try:
                        violation_type = violation.get('violation_type', 'unknown')
                        
                        # Get GPS
                        gps_coords = (0.0, 0.0)
                        if self.gps_reader:
                            location = self.gps_reader.get_location()
                            if location:
                                gps_coords = (location.latitude, location.longitude)
                        
                        # Get speed info if available
                        speed_info = ""
                        if violation_type == 'overspeed':
                            speed_kmh = violation.get('speed_kmh', 0)
                            speed_limit = violation.get('speed_limit', 0)
                            speed_info = f" | Speed: {speed_kmh:.1f}/{speed_limit} km/h"
                        
                        # Log violation
                        logger.info(
                            f"VIOLATION: {violation_type}{speed_info} | "
                            f"GPS: {gps_coords[0]:.6f},{gps_coords[1]:.6f}"
                        )
                        
                        self.stats['plates_read'] += 1
                    
                    except Exception as e:
                        logger.error(f"Error processing violation: {e}")
                
                # Periodic storage cleanup (every 100 violations)
                cleanup_counter += len(result.violations)
                if cleanup_counter >= 100 and self.storage_manager:
                    self.storage_manager.check_and_cleanup()
                    cleanup_counter = 0
            
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Logging thread error: {e}")
        
        logger.info("Logging thread stopped")
    
    def _display_loop(self):
        """Display loop"""
        logger.info("Display loop started")
        
        window_name = "Edge Traffic Violation Detection - Press 'q' to quit"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        
        while not self.stop_event.is_set():
            try:
                frame = None
                try:
                    while True:
                        result = self.result_queue.get_nowait()
                        frame = result.frame
                except queue.Empty:
                    pass
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Draw overlay
                cv2.putText(
                    frame,
                    f"Violations: {self.stats['violations_detected']}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )
                
                # Draw speed violations count
                cv2.putText(
                    frame,
                    f"Speed: {self.stats['speed_violations']}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 165, 255),
                    2
                )
                
                cv2.imshow(window_name, frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("User pressed 'q', stopping pipeline")
                    break
            
            except Exception as e:
                logger.error(f"Display loop error: {e}")
        
        cv2.destroyAllWindows()
        logger.info("Display loop stopped")
    
    def _print_startup_summary(self):
        """Print startup summary"""
        logger.info("=" * 70)
        logger.info("EDGE TRAFFIC VIOLATION DETECTION - STARTUP")
        logger.info("=" * 70)
        logger.info(f"Camera: {self.camera_source}")
        logger.info(f"Display: {self.show_display}")
        logger.info("=" * 70)
    
    def _print_session_summary(self):
        """Print session summary"""
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        logger.info("=" * 70)
        logger.info("EDGE TRAFFIC VIOLATION DETECTION - SESSION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Uptime: {int(uptime)} seconds")
        logger.info(f"Total Frames: {self.stats['total_frames']}")
        logger.info(f"Violations Detected: {self.stats['violations_detected']}")
        logger.info(f"Speed Violations: {self.stats['speed_violations']}")
        logger.info("=" * 70)
        
        # Print speed detector stats if available
        if self.speed_detector:
            self.speed_detector.print_stats()
