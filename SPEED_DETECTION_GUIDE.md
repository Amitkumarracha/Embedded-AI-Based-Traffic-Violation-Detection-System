# Speed Detection Integration Guide

## Overview

This guide explains how to use the integrated speed detection system for the helmet-mounted Raspberry Pi traffic violation detection system.

## Architecture

```
Video Input (Webcam)
    ↓
Vehicle Detection (YOLO)
    ↓
Vehicle Tracking (DeepSort)
    ↓
Speed Estimation (Overhead Calibration)
    ↓
Violation Detection (Speed Threshold)
    ↓
Evidence Generation (Frame + GPS + Speed)
    ↓
PDF Report + Video Output
```

## Key Components

### 1. Speed Detector (`edge_core/speed_detector.py`)

**Main Classes:**
- `SpeedDetector`: Main speed estimation and violation detection
- `SpeedConfig`: Configuration for speed detection
- `SpeedBuffer`: Moving average smoothing for speed measurements
- `OverheadSpeedCalibrator`: Converts pixel displacement to real-world speed

**Key Features:**
- Overhead camera calibration (pixels per meter)
- Real-time speed calculation from tracking data
- Moving average smoothing to reduce noise
- Configurable speed limits and violation thresholds
- Track-based speed history

### 2. Integration Points

The speed detector is integrated into the main pipeline at:

**`edge_pipeline/main_pipeline.py`:**
- Initialized in `_init_components()`
- Processes tracks in `_inference_thread()`
- Generates speed violations
- Draws speed overlays on frames

## Configuration

### Environment Variables (`.env.rpi`)

```bash
# Speed Detection Configuration
PIXELS_PER_METER=8.0                    # Camera calibration
SPEED_LIMIT_KMH=60.0                    # Speed limit
SPEED_VIOLATION_THRESHOLD=60.0          # Violation threshold
MIN_TRACK_LENGTH_SPEED=5                # Min frames for calculation
```

### Camera Calibration

**To calibrate your camera:**

1. **Measure a known distance** in your camera's field of view (e.g., 5 meters)
2. **Count pixels** corresponding to that distance in the frame
3. **Calculate pixels per meter:**
   ```
   pixels_per_meter = pixel_distance / known_distance_meters
   ```

**Example:**
- Known distance: 5 meters
- Pixel distance: 40 pixels
- Calibration: 40 / 5 = **8 pixels/meter**

**Calibration Script:**
```python
from edge_core.speed_detector import calibrate_from_video

ppm = calibrate_from_video(
    video_path="calibration.mp4",
    known_distance_meters=5.0,
    point1=(100, 200),  # Start point
    point2=(140, 200)   # End point (40 pixels away)
)
print(f"Pixels per meter: {ppm}")
```

## Usage

### 1. Basic Speed Detection

```python
from edge_core.speed_detector import SpeedDetector, SpeedConfig

# Configure
config = SpeedConfig(
    pixels_per_meter=8.0,
    fps=30.0,
    speed_limit_kmh=60.0,
    violation_threshold_kmh=60.0,
    min_track_length=5,
    smoothing_window=5,
)

# Initialize
detector = SpeedDetector(config=config)

# Process tracks
speed_results = detector.process_tracks(
    tracks=tracked_objects,
    frame_id=current_frame_id,
    timestamp=current_timestamp
)

# Check results
for track_id, speed_data in speed_results.items():
    print(f"Track {track_id}: {speed_data['speed_kmh']:.1f} km/h")
    if speed_data['is_violation']:
        print(f"  VIOLATION! Limit: {speed_data['speed_limit']} km/h")
```

### 2. Integration with Pipeline

The speed detector is automatically integrated when you run the edge pipeline:

```bash
# Start edge pipeline with speed detection
python run_edge.py
```

The pipeline will:
1. Detect vehicles using YOLO
2. Track vehicles using DeepSort
3. Calculate speed for each tracked vehicle
4. Detect speed violations
5. Log violations with GPS coordinates
6. Display speed overlays on video

### 3. Testing Speed Detection

**Test with video file:**
```bash
cd scripts
python test_speed_detection.py --video input.mp4 --output output.mp4
```

**Test basic calculation:**
```bash
python test_speed_detection.py --basic
```

## Speed Calculation Formula

### From Tracking Data

```
1. Pixel Displacement:
   pixel_distance = sqrt((x2 - x1)² + (y2 - y1)²)

2. Real-World Distance:
   meters = pixel_distance / pixels_per_meter

3. Time Elapsed:
   time_seconds = frames / fps

4. Speed:
   speed_m/s = meters / time_seconds
   speed_km/h = speed_m/s × 3.6
```

### Example Calculation

**Given:**
- Pixels per meter: 8
- FPS: 30
- Movement: 10 pixels per frame

**Calculation:**
```
1. Pixel distance per frame: 10 pixels
2. Meters per frame: 10 / 8 = 1.25 meters
3. Time per frame: 1 / 30 = 0.0333 seconds
4. Speed: 1.25 / 0.0333 = 37.5 m/s
5. Speed in km/h: 37.5 × 3.6 = 135 km/h
```

## Violation Detection

### Violation Criteria

A speed violation is detected when:
1. Track has minimum required frames (default: 5)
2. Speed exceeds violation threshold
3. Track is confirmed by tracker

### Violation Data

Each violation includes:
```python
{
    'violation_type': 'overspeed',
    'track_id': 123,
    'speed_kmh': 85.5,
    'speed_limit': 60.0,
    'bbox': (x1, y1, x2, y2),
    'position': (cx, cy),
    'timestamp': 1234567890.123,
    'gps_coords': (18.5204, 73.8567),
}
```

## Visualization

### Speed Overlay

The system draws speed information on each tracked vehicle:

**Normal Speed (Green):**
```
ID:123 45.5 km/h
```

**Violation (Red):**
```
OVERSPEED!
ID:123 85.5 km/h
```

### Display Elements

- **Top-left:** Total violations count
- **Below:** Speed violations count
- **On vehicles:** Individual speed and ID
- **Violation indicator:** Red "OVERSPEED!" text

## Performance Optimization

### For Raspberry Pi 5

**Recommended Settings:**
```bash
# .env.rpi
PIXELS_PER_METER=8.0
MIN_TRACK_LENGTH_SPEED=5      # Faster detection
SMOOTHING_WINDOW=3            # Less smoothing, faster response
PROCESS_EVERY_N_FRAMES=1      # Process all frames
```

### For Lower-End Hardware

```bash
# .env.rpi
MIN_TRACK_LENGTH_SPEED=10     # More stable, slower detection
SMOOTHING_WINDOW=7            # More smoothing
PROCESS_EVERY_N_FRAMES=2      # Process every 2nd frame
```

## Troubleshooting

### Issue: Inaccurate Speed Readings

**Solutions:**
1. **Recalibrate camera:**
   - Measure known distance more accurately
   - Use larger reference distance (5-10 meters)
   - Ensure camera is stable and overhead

2. **Adjust smoothing:**
   - Increase `smoothing_window` for more stable readings
   - Decrease for faster response to speed changes

3. **Check FPS:**
   - Verify actual camera FPS matches configuration
   - Use `camera_fps` setting in `.env.rpi`

### Issue: Too Many False Violations

**Solutions:**
1. **Increase violation threshold:**
   ```bash
   SPEED_VIOLATION_THRESHOLD=70.0  # Instead of 60.0
   ```

2. **Increase minimum track length:**
   ```bash
   MIN_TRACK_LENGTH_SPEED=10  # Instead of 5
   ```

3. **Increase smoothing:**
   ```bash
   # In SpeedConfig
   smoothing_window=7  # Instead of 5
   ```

### Issue: Speed Not Detected

**Solutions:**
1. **Check tracking:**
   - Ensure vehicles are being tracked
   - Verify tracker is initialized

2. **Check displacement:**
   - Vehicles must move minimum distance
   - Default: 10 pixels minimum

3. **Check configuration:**
   - Verify `pixels_per_meter` is set correctly
   - Check FPS matches video/camera

## Advanced Features

### Custom Speed Zones

You can implement different speed limits for different areas:

```python
def get_speed_limit_for_zone(position):
    """Get speed limit based on position"""
    x, y = position
    
    # School zone (left side)
    if x < 400:
        return 30.0
    # Highway (right side)
    elif x > 800:
        return 100.0
    # Default
    else:
        return 60.0

# In speed detection loop
for track_id, speed_data in speed_results.items():
    zone_limit = get_speed_limit_for_zone(speed_data['position'])
    if speed_data['speed_kmh'] > zone_limit:
        # Custom violation handling
        pass
```

### Speed History Analysis

```python
# Get speed history for a track
history = detector.position_history[track_id]
speeds = []

for i in range(1, len(history)):
    prev_pos = history[i-1]
    curr_pos = history[i]
    speed = detector.calibrator.calculate_speed(
        prev_pos, curr_pos, 1/30.0
    )
    speeds.append(speed)

# Analyze
avg_speed = sum(speeds) / len(speeds)
max_speed = max(speeds)
print(f"Average: {avg_speed:.1f} km/h, Max: {max_speed:.1f} km/h")
```

## API Reference

### SpeedDetector

**Methods:**
- `update_track(track_id, position, timestamp)` - Update track and calculate speed
- `check_violation(track_id, speed_kmh, frame_id)` - Check for violation
- `process_tracks(tracks, frame_id, timestamp)` - Process all tracks
- `get_violation_summary(track_id)` - Get violation details
- `cleanup_track(track_id)` - Clean up lost track
- `reset()` - Reset all data
- `get_stats()` - Get statistics
- `print_stats()` - Print statistics

### SpeedConfig

**Parameters:**
- `pixels_per_meter` (float): Camera calibration
- `fps` (float): Video frame rate
- `speed_limit_kmh` (float): Speed limit
- `violation_threshold_kmh` (float): Violation threshold
- `min_track_length` (int): Minimum frames for calculation
- `smoothing_window` (int): Moving average window
- `min_displacement` (float): Minimum pixel movement

## Examples

### Example 1: Simple Speed Detection

```python
from edge_core.speed_detector import SpeedDetector, SpeedConfig

config = SpeedConfig(pixels_per_meter=8.0, fps=30.0)
detector = SpeedDetector(config=config)

# Simulate movement
for frame in range(30):
    position = (100 + frame * 10, 200)
    timestamp = frame / 30.0
    
    speed = detector.update_track(1, position, timestamp)
    if speed:
        print(f"Speed: {speed:.1f} km/h")
```

### Example 2: Video Processing

See `scripts/test_speed_detection.py` for complete example.

### Example 3: Real-time Camera

```python
from edge_pipeline.main_pipeline import EdgePipeline

# Start pipeline with speed detection
pipeline = EdgePipeline(camera_source=0, show_display=True)
pipeline.start()
```

## References

- **Speed Detection Module:** `edge_core/speed_detector.py`
- **Pipeline Integration:** `edge_pipeline/main_pipeline.py`
- **Configuration:** `edge_config/settings.py`
- **Test Script:** `scripts/test_speed_detection.py`
- **Environment:** `.env.rpi`

## Support

For issues or questions:
1. Check this guide
2. Review test scripts
3. Check logs in `logs/` directory
4. Verify calibration settings

---

**Last Updated:** 2026-04-30
**Version:** 1.0.0
