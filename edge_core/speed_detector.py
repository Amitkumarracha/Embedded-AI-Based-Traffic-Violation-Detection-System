#!/usr/bin/env python3
"""
Speed Detection Module for Edge Deployment
Estimates vehicle speed using overhead camera calibration and tracking data
Integrated with helmet-mounted Raspberry Pi system
"""

import numpy as np
import cv2
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from collections import deque
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class SpeedConfig:
    """Speed detection configuration for overhead camera"""
    pixels_per_meter: float = 8.0           # Calibration: pixels per meter (from your code)
    fps: float = 30.0                        # Video FPS
    speed_limit_kmh: float = 60.0            # Default speed limit
    violation_threshold_kmh: float = 60.0    # Speed violation threshold
    min_track_length: int = 5                # Minimum frames for speed calculation
    smoothing_window: int = 5                # Moving average window for speed smoothing
    min_displacement: float = 10.0           # Minimum pixel displacement to calculate speed


class SpeedBuffer:
    """
    Speed buffer for smoothing speed measurements
    Uses moving average to reduce noise
    """
    
    def __init__(self, size: int = 5):
        """
        Initialize speed buffer
        
        Args:
            size: Buffer size for moving average
        """
        self.buffer = deque(maxlen=size)
    
    def update(self, speed: float) -> float:
        """
        Update buffer and return smoothed speed
        
        Args:
            speed: Current speed measurement
        
        Returns:
            Smoothed speed (moving average)
        """
        self.buffer.append(speed)
        return sum(self.buffer) / len(self.buffer)
    
    def reset(self):
        """Clear buffer"""
        self.buffer.clear()


class OverheadSpeedCalibrator:
    """
    Speed calculator for overhead camera view
    Converts pixel displacement to real-world speed
    """
    
    def __init__(self, ppm: float = 8.0):
        """
        Initialize speed calibrator
        
        Args:
            ppm: Pixels per meter (calibration value)
        """
        self.ppm = ppm
        logger.info(f"SpeedCalibrator initialized with {ppm} pixels/meter")
    
    def calculate_speed(
        self,
        prev: Tuple[int, int],
        curr: Tuple[int, int],
        time_diff: float
    ) -> float:
        """
        Calculate speed from two positions
        
        Args:
            prev: Previous position (x, y)
            curr: Current position (x, y)
            time_diff: Time difference in seconds
        
        Returns:
            Speed in km/h
        """
        if time_diff <= 0:
            return 0.0
        
        # Calculate pixel distance
        pixel_dist = np.linalg.norm(np.array(curr) - np.array(prev))
        
        # Convert to meters
        meters = pixel_dist / self.ppm
        
        # Calculate speed in m/s
        speed_mps = meters / time_diff
        
        # Convert to km/h
        speed_kmh = speed_mps * 3.6
        
        return speed_kmh
    
    def calibrate(self, known_distance_meters: float, pixel_distance: float):
        """
        Calibrate pixels per meter using known distance
        
        Args:
            known_distance_meters: Real-world distance in meters
            pixel_distance: Corresponding pixel distance
        """
        self.ppm = pixel_distance / known_distance_meters
        logger.info(f"Calibrated to {self.ppm:.2f} pixels/meter")


class SpeedDetector:
    """
    Vehicle speed estimation and violation detection
    Integrates with existing tracker for real-time speed monitoring
    """
    
    def __init__(self, config: Optional[SpeedConfig] = None):
        """
        Initialize speed detector
        
        Args:
            config: Speed detection configuration
        """
        self.config = config or SpeedConfig()
        
        # Speed calculator
        self.calibrator = OverheadSpeedCalibrator(ppm=self.config.pixels_per_meter)
        
        # Track speed buffers for smoothing
        self.speed_buffers: Dict[int, SpeedBuffer] = {}
        
        # Track position history
        self.position_history: Dict[int, deque] = {}
        
        # Track time history
        self.time_history: Dict[int, deque] = {}
        
        # Violation tracking
        self.violations: Dict[int, dict] = {}
        
        # Statistics
        self.stats = {
            'total_measurements': 0,
            'total_violations': 0,
            'max_speed_detected': 0.0,
        }
        
        logger.info(f"SpeedDetector initialized")
        logger.info(f"  Speed limit: {self.config.speed_limit_kmh} km/h")
        logger.info(f"  Violation threshold: {self.config.violation_threshold_kmh} km/h")
        logger.info(f"  Pixels per meter: {self.config.pixels_per_meter}")
    
    def update_track(
        self,
        track_id: int,
        position: Tuple[int, int],
        timestamp: float
    ) -> Optional[float]:
        """
        Update track position and calculate speed
        
        Args:
            track_id: Track ID
            position: Current position (x, y)
            timestamp: Current timestamp
        
        Returns:
            Smoothed speed in km/h, or None if insufficient data
        """
        # Initialize buffers for new track
        if track_id not in self.speed_buffers:
            self.speed_buffers[track_id] = SpeedBuffer(size=self.config.smoothing_window)
            self.position_history[track_id] = deque(maxlen=self.config.min_track_length)
            self.time_history[track_id] = deque(maxlen=self.config.min_track_length)
        
        # Store position and time
        self.position_history[track_id].append(position)
        self.time_history[track_id].append(timestamp)
        
        # Need at least 2 positions to calculate speed
        if len(self.position_history[track_id]) < 2:
            return None
        
        # Get previous position and time
        prev_pos = self.position_history[track_id][-2]
        prev_time = self.time_history[track_id][-2]
        
        # Calculate time difference
        time_diff = timestamp - prev_time
        
        if time_diff <= 0:
            return None
        
        # Calculate pixel displacement
        pixel_dist = np.linalg.norm(np.array(position) - np.array(prev_pos))
        
        # Skip if displacement too small (stationary or noise)
        if pixel_dist < self.config.min_displacement:
            return 0.0
        
        # Calculate instantaneous speed
        speed = self.calibrator.calculate_speed(prev_pos, position, time_diff)
        
        # Apply smoothing
        smoothed_speed = self.speed_buffers[track_id].update(speed)
        
        # Update statistics
        self.stats['total_measurements'] += 1
        self.stats['max_speed_detected'] = max(
            self.stats['max_speed_detected'],
            smoothed_speed
        )
        
        return smoothed_speed
    
    def check_violation(
        self,
        track_id: int,
        speed_kmh: float,
        frame_id: int
    ) -> bool:
        """
        Check if speed exceeds violation threshold
        
        Args:
            track_id: Track ID
            speed_kmh: Vehicle speed in km/h
            frame_id: Current frame ID
        
        Returns:
            True if violation detected
        """
        is_violation = speed_kmh > self.config.violation_threshold_kmh
        
        if is_violation:
            # Record violation
            if track_id not in self.violations:
                self.violations[track_id] = {
                    'first_frame': frame_id,
                    'max_speed': speed_kmh,
                    'violation_count': 1,
                    'first_detected': time.time(),
                }
                self.stats['total_violations'] += 1
                
                logger.warning(
                    f"SPEED VIOLATION: Track {track_id} @ {speed_kmh:.1f} km/h "
                    f"(limit: {self.config.violation_threshold_kmh} km/h)"
                )
            else:
                # Update existing violation
                self.violations[track_id]['max_speed'] = max(
                    self.violations[track_id]['max_speed'],
                    speed_kmh
                )
                self.violations[track_id]['violation_count'] += 1
        
        return is_violation
    
    def process_tracks(
        self,
        tracks: List,
        frame_id: int,
        timestamp: float
    ) -> Dict[int, dict]:
        """
        Process all tracks and detect speed violations
        
        Args:
            tracks: List of TrackedObject from tracker
            frame_id: Current frame ID
            timestamp: Current timestamp
        
        Returns:
            Dict of {track_id: {'speed': float, 'violation': bool, ...}}
        """
        results = {}
        
        for track in tracks:
            track_id = track.track_id
            
            # Get centroid position
            position = (track.center_x, track.center_y)
            
            # Update track and calculate speed
            speed = self.update_track(track_id, position, timestamp)
            
            if speed is None:
                continue
            
            # Check violation
            is_violation = self.check_violation(track_id, speed, frame_id)
            
            results[track_id] = {
                'speed_kmh': speed,
                'is_violation': is_violation,
                'speed_limit': self.config.speed_limit_kmh,
                'violation_threshold': self.config.violation_threshold_kmh,
                'position': position,
            }
        
        return results
    
    def get_violation_summary(self, track_id: int) -> Optional[dict]:
        """
        Get violation summary for a track
        
        Args:
            track_id: Track ID
        
        Returns:
            Violation summary dict or None
        """
        if track_id not in self.violations:
            return None
        
        return self.violations[track_id].copy()
    
    def cleanup_track(self, track_id: int):
        """
        Clean up data for lost track
        
        Args:
            track_id: Track ID to clean up
        """
        if track_id in self.speed_buffers:
            del self.speed_buffers[track_id]
        if track_id in self.position_history:
            del self.position_history[track_id]
        if track_id in self.time_history:
            del self.time_history[track_id]
    
    def reset(self):
        """Reset all tracking data"""
        self.speed_buffers.clear()
        self.position_history.clear()
        self.time_history.clear()
        self.violations.clear()
        logger.info("SpeedDetector reset")
    
    def get_stats(self) -> dict:
        """Get detector statistics"""
        return {
            'total_measurements': self.stats['total_measurements'],
            'total_violations': self.stats['total_violations'],
            'max_speed_detected': self.stats['max_speed_detected'],
            'active_tracks': len(self.speed_buffers),
            'speed_limit': self.config.speed_limit_kmh,
            'violation_threshold': self.config.violation_threshold_kmh,
        }
    
    def print_stats(self):
        """Pretty-print detector statistics"""
        stats = self.get_stats()
        
        print("""
╔════════════════════════════════════════════════════╗
║          SPEED DETECTOR STATISTICS                 ║
╚════════════════════════════════════════════════════╝
""")
        print(f"Total Measurements:    {stats['total_measurements']}")
        print(f"Total Violations:      {stats['total_violations']}")
        print(f"Max Speed Detected:    {stats['max_speed_detected']:.1f} km/h")
        print(f"Active Tracks:         {stats['active_tracks']}")
        print(f"Speed Limit:           {stats['speed_limit']} km/h")
        print(f"Violation Threshold:   {stats['violation_threshold']} km/h")
        print("""
════════════════════════════════════════════════════╗
        """)


# ==============================================
# UTILITY FUNCTIONS
# ==============================================

def calibrate_from_video(
    video_path: str,
    known_distance_meters: float,
    point1: Tuple[int, int],
    point2: Tuple[int, int]
) -> float:
    """
    Calibrate pixels per meter from video with known distance
    
    Args:
        video_path: Path to calibration video
        known_distance_meters: Known real-world distance
        point1: First point (x, y)
        point2: Second point (x, y)
    
    Returns:
        Pixels per meter calibration value
    """
    pixel_distance = np.linalg.norm(np.array(point2) - np.array(point1))
    ppm = pixel_distance / known_distance_meters
    
    logger.info(f"Calibration: {pixel_distance:.1f} pixels = {known_distance_meters} meters")
    logger.info(f"Result: {ppm:.2f} pixels/meter")
    
    return ppm


def draw_speed_overlay(
    frame: np.ndarray,
    track_id: int,
    position: Tuple[int, int],
    speed: float,
    is_violation: bool = False
) -> np.ndarray:
    """
    Draw speed information on frame
    
    Args:
        frame: Input frame
        track_id: Track ID
        position: Position (x, y)
        speed: Speed in km/h
        is_violation: Whether this is a violation
    
    Returns:
        Annotated frame
    """
    x, y = position
    
    # Choose color based on violation
    color = (0, 0, 255) if is_violation else (0, 255, 0)
    
    # Draw speed text
    text = f"ID:{track_id} {speed:.1f} km/h"
    cv2.putText(
        frame,
        text,
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )
    
    # Draw violation indicator
    if is_violation:
        cv2.putText(
            frame,
            "OVERSPEED!",
            (x, y - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2
        )
    
    return frame


# ==============================================
# MAIN / TESTING
# ==============================================

if __name__ == "__main__":
    print("Testing SpeedDetector module...\n")
    
    # Initialize detector
    config = SpeedConfig(
        pixels_per_meter=8.0,
        fps=30.0,
        speed_limit_kmh=60.0,
        violation_threshold_kmh=60.0,
    )
    
    detector = SpeedDetector(config)
    
    # Simulate track movement
    print("Simulating vehicle movement...\n")
    
    track_id = 1
    start_time = time.time()
    
    # Simulate 30 frames of movement (1 second at 30 FPS)
    for frame_idx in range(30):
        # Simulate movement: 10 pixels per frame (moving right)
        position = (100 + frame_idx * 10, 200)
        timestamp = start_time + (frame_idx / 30.0)
        
        # Update track
        speed = detector.update_track(track_id, position, timestamp)
        
        if speed is not None:
            # Check violation
            is_violation = detector.check_violation(track_id, speed, frame_idx)
            
            if frame_idx % 10 == 0:
                print(f"Frame {frame_idx}: Speed = {speed:.1f} km/h, Violation = {is_violation}")
    
    # Print statistics
    print()
    detector.print_stats()
    
    # Get violation summary
    violation_summary = detector.get_violation_summary(track_id)
    if violation_summary:
        print(f"\nViolation Summary for Track {track_id}:")
        print(f"  Max Speed: {violation_summary['max_speed']:.1f} km/h")
        print(f"  Violation Count: {violation_summary['violation_count']}")
    
    print("\n✅ SpeedDetector test complete!")
