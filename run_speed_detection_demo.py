#!/usr/bin/env python3
"""
Speed Detection Demo
Quick demonstration of speed detection capabilities
"""

import cv2
import numpy as np
import time
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from edge_core.speed_detector import (
    SpeedDetector,
    SpeedConfig,
    draw_speed_overlay,
    OverheadSpeedCalibrator
)


class SimpleTrack:
    """Simple track object for demo"""
    def __init__(self, track_id, x, y, w=50, h=50):
        self.track_id = track_id
        self.center_x = x
        self.center_y = y
        self.x1 = x - w // 2
        self.y1 = y - h // 2
        self.x2 = x + w // 2
        self.y2 = y + h // 2


def create_demo_frame(width=1280, height=720):
    """Create a demo frame with road"""
    frame = np.ones((height, width, 3), dtype=np.uint8) * 50
    
    # Draw road
    cv2.rectangle(frame, (0, height//3), (width, 2*height//3), (80, 80, 80), -1)
    
    # Draw lane markings
    for x in range(0, width, 100):
        cv2.rectangle(frame, (x, height//2 - 5), (x + 50, height//2 + 5), (255, 255, 255), -1)
    
    # Draw speed limit sign
    cv2.circle(frame, (100, 100), 40, (255, 255, 255), -1)
    cv2.circle(frame, (100, 100), 35, (255, 0, 0), 3)
    cv2.putText(frame, "60", (75, 110), cv2.FONT_HERSHEY_BOLD, 1, (0, 0, 0), 2)
    
    return frame


def draw_vehicle(frame, x, y, color=(0, 255, 0)):
    """Draw a simple vehicle"""
    # Vehicle body
    cv2.rectangle(frame, (x-25, y-15), (x+25, y+15), color, -1)
    # Windows
    cv2.rectangle(frame, (x-20, y-10), (x-5, y+10), (100, 100, 100), -1)
    cv2.rectangle(frame, (x+5, y-10), (x+20, y+10), (100, 100, 100), -1)


def demo_speed_detection():
    """Run interactive speed detection demo"""
    print("=" * 70)
    print("SPEED DETECTION DEMO")
    print("=" * 70)
    print("This demo simulates vehicles moving at different speeds")
    print("Press 'q' to quit, 's' to save screenshot")
    print("=" * 70)
    
    # Configuration
    width, height = 1280, 720
    fps = 30
    
    # Initialize speed detector
    config = SpeedConfig(
        pixels_per_meter=8.0,
        fps=fps,
        speed_limit_kmh=60.0,
        violation_threshold_kmh=60.0,
        min_track_length=5,
        smoothing_window=5,
    )
    
    detector = SpeedDetector(config=config)
    
    # Create output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('speed_demo_output.mp4', fourcc, fps, (width, height))
    
    # Simulation parameters
    vehicles = [
        {'id': 1, 'start_x': 100, 'speed_pixels': 5, 'y': height//2 - 50, 'color': (0, 255, 0)},   # 67.5 km/h
        {'id': 2, 'start_x': 100, 'speed_pixels': 8, 'y': height//2, 'color': (0, 165, 255)},      # 108 km/h - VIOLATION
        {'id': 3, 'start_x': 100, 'speed_pixels': 3, 'y': height//2 + 50, 'color': (0, 255, 0)},   # 40.5 km/h
    ]
    
    frame_id = 0
    start_time = time.time()
    
    print("\nSimulating 3 vehicles:")
    print("  Vehicle 1 (Green):  ~67.5 km/h (within limit)")
    print("  Vehicle 2 (Orange): ~108 km/h (VIOLATION!)")
    print("  Vehicle 3 (Green):  ~40.5 km/h (within limit)")
    print()
    
    # Run simulation
    while True:
        frame_id += 1
        timestamp = time.time()
        
        # Create frame
        frame = create_demo_frame(width, height)
        
        # Update and draw vehicles
        tracks = []
        for vehicle in vehicles:
            # Calculate position
            x = vehicle['start_x'] + (frame_id * vehicle['speed_pixels'])
            y = vehicle['y']
            
            # Reset if off screen
            if x > width + 50:
                vehicle['start_x'] = -50
                x = vehicle['start_x']
                # Clean up old track
                detector.cleanup_track(vehicle['id'])
            
            # Draw vehicle
            draw_vehicle(frame, x, y, vehicle['color'])
            
            # Create track
            track = SimpleTrack(vehicle['id'], x, y)
            tracks.append(track)
        
        # Process speed detection
        speed_results = detector.process_tracks(tracks, frame_id, timestamp)
        
        # Draw speed overlays
        for track_id, speed_data in speed_results.items():
            draw_speed_overlay(
                frame,
                track_id,
                speed_data['position'],
                speed_data['speed_kmh'],
                speed_data['is_violation']
            )
        
        # Draw info panel
        info_y = 30
        cv2.putText(frame, f"Frame: {frame_id}", (10, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        info_y += 30
        cv2.putText(frame, f"Speed Limit: {config.speed_limit_kmh} km/h", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        info_y += 30
        stats = detector.get_stats()
        cv2.putText(frame, f"Violations: {stats['total_violations']}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        info_y += 30
        cv2.putText(frame, f"Max Speed: {stats['max_speed_detected']:.1f} km/h", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Draw legend
        legend_x = width - 300
        legend_y = 30
        cv2.putText(frame, "Legend:", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        legend_y += 25
        cv2.putText(frame, "Green = Within Limit", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        legend_y += 20
        cv2.putText(frame, "Red = OVERSPEED", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Draw calibration info
        calib_y = height - 60
        cv2.putText(frame, f"Calibration: {config.pixels_per_meter} pixels/meter", 
                   (10, calib_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        calib_y += 20
        cv2.putText(frame, f"FPS: {config.fps}", 
                   (10, calib_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        calib_y += 20
        cv2.putText(frame, "Press 'q' to quit, 's' to save screenshot", 
                   (10, calib_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Write to video
        out.write(frame)
        
        # Display
        cv2.imshow("Speed Detection Demo", frame)
        
        # Handle keyboard
        key = cv2.waitKey(int(1000/fps)) & 0xFF
        if key == ord('q'):
            print("\nStopping demo...")
            break
        elif key == ord('s'):
            screenshot_path = f"speed_demo_screenshot_{frame_id}.jpg"
            cv2.imwrite(screenshot_path, frame)
            print(f"Screenshot saved: {screenshot_path}")
        
        # Stop after 300 frames (10 seconds)
        if frame_id >= 300:
            print("\nDemo complete (10 seconds)")
            break
    
    # Cleanup
    out.release()
    cv2.destroyAllWindows()
    
    # Print final statistics
    print("\n" + "=" * 70)
    print("DEMO RESULTS")
    print("=" * 70)
    
    detector.print_stats()
    
    # Print individual violation summaries
    print("\nViolation Details:")
    for vehicle in vehicles:
        summary = detector.get_violation_summary(vehicle['id'])
        if summary:
            print(f"\n  Vehicle {vehicle['id']}:")
            print(f"    Max Speed: {summary['max_speed']:.1f} km/h")
            print(f"    Violation Count: {summary['violation_count']}")
            print(f"    First Frame: {summary['first_frame']}")
    
    print("\n" + "=" * 70)
    print("Output saved to: speed_demo_output.mp4")
    print("=" * 70)


def demo_calibration():
    """Demonstrate camera calibration"""
    print("=" * 70)
    print("CAMERA CALIBRATION DEMO")
    print("=" * 70)
    
    # Example calibration scenarios
    scenarios = [
        {"name": "Close Range", "distance_m": 3, "pixels": 24},
        {"name": "Medium Range", "distance_m": 5, "pixels": 40},
        {"name": "Far Range", "distance_m": 10, "pixels": 80},
    ]
    
    print("\nCalibration Examples:")
    print("-" * 70)
    
    for scenario in scenarios:
        ppm = scenario['pixels'] / scenario['distance_m']
        print(f"\n{scenario['name']}:")
        print(f"  Known Distance: {scenario['distance_m']} meters")
        print(f"  Pixel Distance: {scenario['pixels']} pixels")
        print(f"  Calibration: {ppm:.2f} pixels/meter")
        
        # Calculate example speed
        pixels_per_frame = 10
        fps = 30
        speed_mps = (pixels_per_frame / ppm) * fps
        speed_kmh = speed_mps * 3.6
        print(f"  Example: 10 pixels/frame @ 30 FPS = {speed_kmh:.1f} km/h")
    
    print("\n" + "=" * 70)
    print("To calibrate your camera:")
    print("1. Measure a known distance in your camera view")
    print("2. Count the pixels for that distance")
    print("3. Calculate: pixels_per_meter = pixels / meters")
    print("4. Update PIXELS_PER_METER in .env.rpi")
    print("=" * 70)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Speed Detection Demo")
    parser.add_argument(
        '--calibration',
        action='store_true',
        help='Show calibration examples'
    )
    
    args = parser.parse_args()
    
    if args.calibration:
        demo_calibration()
    else:
        demo_speed_detection()


if __name__ == "__main__":
    main()
