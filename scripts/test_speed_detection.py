#!/usr/bin/env python3
"""
Test Speed Detection Module
Demonstrates speed detection with video input
"""

import cv2
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edge_core.speed_detector import SpeedDetector, SpeedConfig, draw_speed_overlay
from edge_core.tracker import EdgeTracker
from edge_core.detector import Detector


def test_speed_detection_with_video(video_path: str, output_path: str = "output.mp4"):
    """
    Test speed detection with video file
    
    Args:
        video_path: Path to input video
        output_path: Path to output video
    """
    print("=" * 70)
    print("SPEED DETECTION TEST")
    print("=" * 70)
    print(f"Input Video: {video_path}")
    print(f"Output Video: {output_path}")
    print("=" * 70)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
    print("=" * 70)
    
    # Initialize components
    print("Initializing components...")
    
    # Speed detector configuration
    speed_config = SpeedConfig(
        pixels_per_meter=8.0,      # Adjust based on your camera calibration
        fps=fps,
        speed_limit_kmh=60.0,
        violation_threshold_kmh=60.0,
        min_track_length=5,
        smoothing_window=5,
    )
    
    speed_detector = SpeedDetector(config=speed_config)
    
    # Tracker (simplified - you can integrate with your detector)
    try:
        tracker = EdgeTracker()
        print("✓ Tracker initialized")
    except Exception as e:
        print(f"✗ Tracker initialization failed: {e}")
        print("  Using simple centroid tracker instead")
        tracker = None
    
    # Detector (optional - for full pipeline)
    try:
        detector = Detector(
            model_path="models/speed_detection.pt",
            inference_size=416,
            num_threads=4,
        )
        print("✓ Detector initialized")
    except Exception as e:
        print(f"✗ Detector initialization failed: {e}")
        print("  Skipping detection, using manual tracking")
        detector = None
    
    print("=" * 70)
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Statistics
    stats = {
        'total_frames': 0,
        'violations': 0,
        'max_speed': 0.0,
    }
    
    # Process video
    print("Processing video...")
    frame_id = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_id += 1
        timestamp = time.time()
        
        # Run detection (if available)
        detections = []
        if detector:
            detections = detector.infer(frame)
        
        # Run tracking (if available)
        tracks = []
        if tracker and detections:
            tracks = tracker.update(detections, frame)
        
        # Process speed detection
        if tracks:
            speed_results = speed_detector.process_tracks(
                tracks, frame_id, timestamp
            )
            
            # Draw speed overlays
            for track_id, speed_data in speed_results.items():
                draw_speed_overlay(
                    frame,
                    track_id,
                    speed_data['position'],
                    speed_data['speed_kmh'],
                    speed_data['is_violation']
                )
                
                # Update statistics
                if speed_data['is_violation']:
                    stats['violations'] += 1
                
                stats['max_speed'] = max(stats['max_speed'], speed_data['speed_kmh'])
        
        # Draw frame info
        cv2.putText(
            frame,
            f"Frame: {frame_id}/{total_frames}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        cv2.putText(
            frame,
            f"Violations: {stats['violations']}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        
        # Write frame
        out.write(frame)
        
        # Display (optional)
        cv2.imshow("Speed Detection Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nStopped by user")
            break
        
        stats['total_frames'] += 1
        
        # Progress update
        if frame_id % 100 == 0:
            elapsed = time.time() - start_time
            fps_actual = frame_id / elapsed
            print(f"  Processed {frame_id}/{total_frames} frames ({fps_actual:.1f} FPS)")
    
    # Cleanup
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    # Print results
    elapsed = time.time() - start_time
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total Frames Processed: {stats['total_frames']}")
    print(f"Processing Time: {elapsed:.2f} seconds")
    print(f"Average FPS: {stats['total_frames'] / elapsed:.1f}")
    print(f"Speed Violations: {stats['violations']}")
    print(f"Max Speed Detected: {stats['max_speed']:.1f} km/h")
    print("=" * 70)
    
    # Print speed detector statistics
    speed_detector.print_stats()
    
    print(f"\nOutput saved to: {output_path}")
    print("=" * 70)


def test_speed_calculation():
    """Test basic speed calculation"""
    print("=" * 70)
    print("BASIC SPEED CALCULATION TEST")
    print("=" * 70)
    
    # Initialize speed detector
    config = SpeedConfig(
        pixels_per_meter=8.0,
        fps=30.0,
        speed_limit_kmh=60.0,
        violation_threshold_kmh=60.0,
    )
    
    detector = SpeedDetector(config=config)
    
    # Simulate vehicle movement
    print("\nSimulating vehicle moving at ~108 km/h...")
    print("(10 pixels/frame × 30 FPS × 3.6 / 8 PPM = 135 km/h)")
    print()
    
    track_id = 1
    start_time = time.time()
    
    # Simulate 30 frames (1 second)
    for frame_idx in range(30):
        # Moving 10 pixels per frame (fast vehicle)
        position = (100 + frame_idx * 10, 200)
        timestamp = start_time + (frame_idx / 30.0)
        
        speed = detector.update_track(track_id, position, timestamp)
        
        if speed is not None and frame_idx % 10 == 0:
            is_violation = detector.check_violation(track_id, speed, frame_idx)
            print(f"Frame {frame_idx:2d}: Speed = {speed:6.1f} km/h, Violation = {is_violation}")
    
    print()
    detector.print_stats()
    
    # Get violation summary
    violation_summary = detector.get_violation_summary(track_id)
    if violation_summary:
        print(f"\nViolation Summary for Track {track_id}:")
        print(f"  Max Speed: {violation_summary['max_speed']:.1f} km/h")
        print(f"  Violation Count: {violation_summary['violation_count']}")
        print(f"  First Frame: {violation_summary['first_frame']}")
    
    print("=" * 70)


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Speed Detection Module")
    parser.add_argument(
        '--video',
        type=str,
        help='Path to input video file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output.mp4',
        help='Path to output video file (default: output.mp4)'
    )
    parser.add_argument(
        '--basic',
        action='store_true',
        help='Run basic speed calculation test'
    )
    
    args = parser.parse_args()
    
    if args.basic:
        # Run basic test
        test_speed_calculation()
    elif args.video:
        # Run video test
        test_speed_detection_with_video(args.video, args.output)
    else:
        # Run both tests
        print("Running basic speed calculation test...\n")
        test_speed_calculation()
        
        print("\n\nFor video testing, run:")
        print("  python test_speed_detection.py --video input.mp4 --output output.mp4")


if __name__ == "__main__":
    main()
