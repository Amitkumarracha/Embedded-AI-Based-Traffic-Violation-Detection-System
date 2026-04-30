#!/usr/bin/env python3
"""
Test USB Camera
Quick test script to verify USB webcam is working
"""

import cv2
import sys
import time

def main():
    print("=" * 60)
    print("USB Camera Test")
    print("=" * 60)
    
    # Try to open camera
    source = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    
    print(f"\nTrying to open camera source: {source}")
    print("Using V4L2 backend (Video4Linux)...")
    
    cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print(f"❌ Failed to open camera source: {source}")
        print("\nTroubleshooting:")
        print("1. Check if camera is connected: ls /dev/video*")
        print("2. Check camera permissions: sudo usermod -a -G video $USER")
        print("3. Try different source: python test_camera.py 1")
        return 1
    
    print("✅ Camera opened successfully!")
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"\nCamera Properties:")
    print(f"  Resolution: {width}×{height}")
    print(f"  FPS: {fps}")
    
    print("\nCapturing frames... Press 'q' to quit")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        elapsed = time.time() - start_time
        
        if elapsed >= 1.0:
            measured_fps = frame_count / elapsed
            print(f"Measured FPS: {measured_fps:.1f}")
            frame_count = 0
            start_time = time.time()
        
        # Display frame
        cv2.putText(frame, f"Press 'q' to quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Camera Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✅ Camera test complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
