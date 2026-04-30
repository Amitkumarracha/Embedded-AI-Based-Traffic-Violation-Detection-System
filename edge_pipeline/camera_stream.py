#!/usr/bin/env python3
"""
Edge Camera Stream - USB Webcam Capture
Optimized for Raspberry Pi 5 with V4L2 backend
"""

import cv2
import threading
import queue
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class EdgeCameraStream:
    """Non-blocking USB webcam capture for edge deployment"""
    
    def __init__(self, source: int = 0, width: int = 1280, height: int = 720, fps: int = 30):
        self.source = source
        self.width = width
        self.height = height
        self.target_fps = fps
        
        self.frame_queue = queue.Queue(maxsize=2)
        self.stop_event = threading.Event()
        self.capture_thread: Optional[threading.Thread] = None
        
        self.cap = None
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.measured_fps = 0.0
        
        self._initialize_capture()
        logger.info(f"EdgeCameraStream initialized: {width}×{height} @ {fps}fps")
    
    def _initialize_capture(self):
        """Initialize OpenCV VideoCapture with V4L2"""
        backend = cv2.CAP_V4L2  # Video4Linux for Raspberry Pi
        
        logger.info(f"Initializing camera (source={self.source}, backend=V4L2)...")
        
        try:
            self.cap = cv2.VideoCapture(self.source, backend)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera (source={self.source})")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            logger.info(f"✓ Camera initialized: {self.width}×{self.height} @ {self.target_fps}fps")
        
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
    
    def _capture_loop(self):
        """Main capture loop"""
        logger.info("Capture loop started")
        
        while not self.stop_event.is_set():
            try:
                if self.cap is None:
                    time.sleep(0.1)
                    continue
                
                ret, frame = self.cap.read()
                
                if not ret:
                    time.sleep(0.01)
                    continue
                
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                    except queue.Empty:
                        pass
                
                self._update_fps()
                time.sleep(1.0 / self.target_fps * 0.9)
            
            except Exception as e:
                logger.error(f"Capture loop error: {e}")
                time.sleep(0.1)
        
        logger.info("Capture loop stopped")
    
    def _update_fps(self):
        """Update measured FPS"""
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        
        if elapsed >= 1.0:
            self.measured_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def start(self) -> threading.Thread:
        """Start capture thread"""
        if self.capture_thread is not None:
            logger.warning("Capture thread already running")
            return self.capture_thread
        
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
            name="EdgeCameraCapture"
        )
        
        self.capture_thread.start()
        logger.info("✓ Camera capture thread started")
        time.sleep(0.1)
        
        return self.capture_thread
    
    def read(self) -> Optional[cv2.Mat]:
        """Read latest frame (non-blocking)"""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop capture and release resources"""
        logger.info("Stopping camera stream...")
        
        self.stop_event.set()
        
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=2.0)
        
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                logger.warning(f"Error releasing camera: {e}")
            self.cap = None
        
        logger.info("✓ Camera stream stopped")
    
    def get_fps(self) -> float:
        """Get measured FPS"""
        return self.measured_fps
    
    def is_opened(self) -> bool:
        """Check if camera is open"""
        return self.cap is not None and self.cap.isOpened()
