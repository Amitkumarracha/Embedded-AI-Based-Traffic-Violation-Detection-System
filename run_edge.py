#!/usr/bin/env python3
"""
Edge Deployment - Main Entry Point
Run traffic violation detection on Raspberry Pi 5
"""

import sys
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/edge_system.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Edge Traffic Violation Detection System for Raspberry Pi 5"
    )
    parser.add_argument(
        '--source',
        type=int,
        default=0,
        help='Camera source (0=first USB camera, 1=second USB camera)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='full',
        choices=['full', 'test', 'benchmark'],
        help='Run mode: full (complete system), test (camera only), benchmark (performance test)'
    )
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Run without display (headless mode for RPi without monitor)'
    )
    parser.add_argument(
        '--video',
        type=str,
        default=None,
        help='Input video file for testing (instead of camera)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("EMBEDDED AI-BASED TRAFFIC VIOLATION DETECTION SYSTEM")
    logger.info("Raspberry Pi 5 Edge Deployment")
    logger.info("=" * 70)
    
    # Determine camera source
    camera_source = args.video if args.video else args.source
    show_display = not args.no_display
    
    if args.mode == 'test':
        # Test camera only
        logger.info("Running in TEST mode (camera test only)")
        test_camera(camera_source)
    
    elif args.mode == 'benchmark':
        # Benchmark performance
        logger.info("Running in BENCHMARK mode")
        run_benchmark()
    
    else:
        # Full system
        logger.info("Running in FULL mode (complete detection system)")
        run_full_system(camera_source, show_display)


def test_camera(source):
    """Test camera capture"""
    import cv2
    import time
    
    logger.info(f"Testing camera source: {source}")
    
    cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        logger.error(f"Failed to open camera source: {source}")
        return
    
    logger.info("✓ Camera opened successfully")
    logger.info("Press 'q' to quit")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            logger.error("Failed to read frame")
            break
        
        frame_count += 1
        elapsed = time.time() - start_time
        
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            logger.info(f"Camera FPS: {fps:.1f}")
            frame_count = 0
            start_time = time.time()
        
        cv2.imshow("Camera Test - Press 'q' to quit", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    logger.info("Camera test complete")


def run_benchmark():
    """Run performance benchmark"""
    logger.info("Running performance benchmark...")
    
    try:
        from edge_core.detector import Detector
        from edge_config.settings import get_settings
        
        settings = get_settings()
        
        detector = Detector(
            model_path=settings.yolo_model_path,
            inference_size=settings.inference_size,
            num_threads=settings.num_threads,
        )
        
        results = detector.benchmark(n_frames=100)
        
        logger.info("=" * 70)
        logger.info("BENCHMARK RESULTS")
        logger.info("=" * 70)
        logger.info(f"Frames: {results['n_frames']}")
        logger.info(f"Mean: {results['mean_ms']:.1f} ms/frame")
        logger.info(f"Median: {results['median_ms']:.1f} ms/frame")
        logger.info(f"Min: {results['min_ms']:.1f} ms/frame")
        logger.info(f"Max: {results['max_ms']:.1f} ms/frame")
        logger.info(f"FPS: {results['fps']:.1f}")
        logger.info("=" * 70)
    
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")


def run_full_system(camera_source, show_display):
    """Run full detection system"""
    try:
        from edge_pipeline.main_pipeline import EdgePipeline
        
        pipeline = EdgePipeline(
            camera_source=camera_source,
            show_display=show_display
        )
        
        pipeline.start()
    
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        raise


if __name__ == "__main__":
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
