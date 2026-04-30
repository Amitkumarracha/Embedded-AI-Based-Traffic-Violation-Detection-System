# Speed Detection Quick Reference

## 🚀 Quick Start

```bash
# 1. Run demo
python run_speed_detection_demo.py

# 2. Test with video
python scripts/test_speed_detection.py --video input.mp4

# 3. Start production
python run_edge.py
```

## ⚙️ Configuration

### .env.rpi
```bash
PIXELS_PER_METER=8.0              # Camera calibration
SPEED_LIMIT_KMH=60.0              # Speed limit
SPEED_VIOLATION_THRESHOLD=60.0    # Violation trigger
MIN_TRACK_LENGTH_SPEED=5          # Min frames
```

## 📏 Calibration

### Step 1: Measure
- Place marker at known distance (e.g., 5 meters)
- Capture frame or video

### Step 2: Calculate
```python
pixels_per_meter = pixel_distance / known_distance_meters
```

### Step 3: Update
```bash
# Update .env.rpi
PIXELS_PER_METER=8.0  # Your calculated value
```

## 🧮 Speed Formula

```
speed_km/h = (pixels/frame) × fps × 3.6 / pixels_per_meter
```

### Example
```
10 pixels/frame × 30 fps × 3.6 / 8 ppm = 135 km/h
```

## 💻 Code Usage

### Basic
```python
from edge_core.speed_detector import SpeedDetector, SpeedConfig

config = SpeedConfig(pixels_per_meter=8.0, fps=30.0)
detector = SpeedDetector(config=config)

speed = detector.update_track(track_id, position, timestamp)
is_violation = detector.check_violation(track_id, speed, frame_id)
```

### With Pipeline
```python
# Automatically integrated in EdgePipeline
from edge_pipeline.main_pipeline import EdgePipeline

pipeline = EdgePipeline(camera_source=0, show_display=True)
pipeline.start()
```

## 🎯 Violation Detection

### Criteria
- Track has ≥ 5 frames (configurable)
- Speed > violation threshold
- Track is confirmed

### Output
```python
{
    'violation_type': 'overspeed',
    'track_id': 123,
    'speed_kmh': 85.5,
    'speed_limit': 60.0,
    'position': (x, y),
    'timestamp': 1234567890.123,
}
```

## 🎨 Visualization

### Normal Speed (Green)
```
ID:123 45.5 km/h
```

### Violation (Red)
```
OVERSPEED!
ID:123 85.5 km/h
```

## 🔧 Troubleshooting

### Inaccurate Speeds
```bash
# Recalibrate
PIXELS_PER_METER=10.0  # Adjust value

# Increase smoothing
smoothing_window=7
```

### Too Many Violations
```bash
# Increase threshold
SPEED_VIOLATION_THRESHOLD=70.0

# More stable tracking
MIN_TRACK_LENGTH_SPEED=10
```

### No Speed Detected
```bash
# Check tracking
# Verify vehicles moving
# Lower min_displacement
```

## 📊 Statistics

```python
stats = detector.get_stats()
# Returns:
# - total_measurements
# - total_violations
# - max_speed_detected
# - active_tracks
```

## 🎬 Demo Commands

```bash
# Visual demo
python run_speed_detection_demo.py

# Calibration examples
python run_speed_detection_demo.py --calibration

# Video test
python scripts/test_speed_detection.py --video input.mp4

# Basic test
python scripts/test_speed_detection.py --basic
```

## 📁 Key Files

```
edge_core/speed_detector.py           # Main module
edge_pipeline/main_pipeline.py        # Integration
edge_config/settings.py               # Settings
.env.rpi                              # Configuration
SPEED_DETECTION_GUIDE.md              # Full guide
```

## 🔢 Calibration Examples

| Distance | Pixels | PPM  | 10px/frame Speed |
|----------|--------|------|------------------|
| 3m       | 24     | 8.0  | 135 km/h         |
| 5m       | 40     | 8.0  | 135 km/h         |
| 10m      | 80     | 8.0  | 135 km/h         |

## ⚡ Performance

| Platform      | FPS  | Overhead | Tracks |
|---------------|------|----------|--------|
| Raspberry Pi 5| 25-30| < 5ms    | 10+    |
| Laptop        | 60+  | < 2ms    | 20+    |

## 🎛️ Tuning Parameters

### For Accuracy
```python
smoothing_window=7        # More smoothing
min_track_length=10       # More stable
```

### For Speed
```python
smoothing_window=3        # Less smoothing
min_track_length=5        # Faster detection
```

### For Raspberry Pi
```python
PROCESS_EVERY_N_FRAMES=2  # Process every 2nd frame
smoothing_window=5        # Balanced
```

## 📞 Support

1. Read: `SPEED_DETECTION_GUIDE.md`
2. Test: `scripts/test_speed_detection.py`
3. Demo: `run_speed_detection_demo.py`
4. Logs: `logs/` directory

---

**Quick Reference v1.0** | Last Updated: 2026-04-30
