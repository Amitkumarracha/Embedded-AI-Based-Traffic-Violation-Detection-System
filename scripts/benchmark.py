#!/usr/bin/env python3
"""
Performance Benchmark Script
Test inference speed on Raspberry Pi 5
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edge_core.detector import Detector
from edge_config.settings import get_settings
from edge_config.platform_config import get_platform_config, get_system_stats


def main():
    print("=" * 70)
    print("PERFORMANCE BENCHMARK - Raspberry Pi 5")
    print("=" * 70)
    
    # Get configuration
    settings = get_settings()
    platform_config = get_platform_config()
    
    print(platform_config)
    
    # System stats
    stats = get_system_stats()
    print("\n📊 System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🔥 Initializing detector...")
    
    try:
        detector = Detector(
            model_path=settings.yolo_model_path,
            inference_size=settings.inference_size,
            num_threads=settings.num_threads,
            confidence_threshold=settings.detection_confidence,
        )
        
        print("✅ Detector initialized")
        
        print("\n🚀 Running benchmark (100 frames)...")
        results = detector.benchmark(n_frames=100)
        
        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)
        print(f"Frames:        {results['n_frames']}")
        print(f"Mean:          {results['mean_ms']:.1f} ms/frame")
        print(f"Median:        {results['median_ms']:.1f} ms/frame")
        print(f"Min:           {results['min_ms']:.1f} ms/frame")
        print(f"Max:           {results['max_ms']:.1f} ms/frame")
        print(f"FPS:           {results['fps']:.1f}")
        print("=" * 70)
        
        # Performance rating
        fps = results['fps']
        if fps >= 20:
            rating = "🟢 EXCELLENT - Real-time capable"
        elif fps >= 15:
            rating = "🟡 GOOD - Acceptable for real-time"
        elif fps >= 10:
            rating = "🟠 FAIR - May have latency"
        else:
            rating = "🔴 POOR - Consider optimization"
        
        print(f"\nPerformance Rating: {rating}")
        
        # Recommendations
        if fps < 15:
            print("\n💡 Optimization Recommendations:")
            print("  • Use INT8 quantized model (if not already)")
            print("  • Reduce inference size (e.g., 320×320 → 256×256)")
            print("  • Process every 2nd or 3rd frame")
            print("  • Ensure active cooling is working")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
