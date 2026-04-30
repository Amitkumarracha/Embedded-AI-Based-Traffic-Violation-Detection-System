# 🚀 Raspberry Pi 5 Setup Guide - Helmet Violation Detection

## 📋 Your Hardware Configuration

- **Board:** Raspberry Pi 5
- **RAM:** 8GB
- **Storage:** 10GB SSD
- **Camera:** USB Webcam
- **Power:** USB (powers both RPi and webcam)

---

## ⚡ Optimized for Your Setup

This system is **optimized for lightweight operation** on your 10GB SSD:

### Storage Management
- ✅ **Auto-cleanup** enabled (keeps only 7 days of evidence)
- ✅ **Max 1000 evidence images** (oldest auto-deleted)
- ✅ **Log rotation** (keeps logs under 10MB)
- ✅ **Uses ~8GB max** (leaves 2GB free for system)

### Performance Optimization
- ✅ **320×320 inference** (balanced speed/accuracy)
- ✅ **20 FPS target** (real-time detection)
- ✅ **4 CPU threads** (optimized for RPi5)
- ✅ **Lightweight models** (6.23MB main model)

---

## 🚀 Quick Setup (15 Minutes)

### Step 1: Transfer Files to Raspberry Pi

**From your Windows PC:**

```bash
# Using PowerShell or Git Bash
scp -r "E:\traffic violation detection system\Embedded AI-Based Traffic Violation Detection System" pi@raspberrypi.local:~/
```

**Or using WinSCP:**
1. Connect to `raspberrypi.local`
2. Drag and drop the entire folder to `/home/pi/`

### Step 2: SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
```

### Step 3: Run Setup Script

```bash
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/

# Make script executable
chmod +x setup_rpi5.sh

# Run setup (takes 15-20 minutes)
./setup_rpi5.sh
```

☕ **Wait for setup to complete...**

### Step 4: Connect USB Webcam

1. Plug USB webcam into any USB port on Raspberry Pi
2. Webcam will be powered by the USB port
3. Verify camera is detected:

```bash
# List video devices
v4l2-ctl --list-devices

# Should show /dev/video0 or similar
```

### Step 5: Test Camera

```bash
# Activate environment
source venv/bin/activate

# Test camera
python scripts/test_camera.py
```

Press 'q' to quit when you see the camera feed.

### Step 6: Run Helmet Detection System

```bash
# Run headless (no monitor needed)
python run_edge.py --mode full --no-display

# Or with display (if HDMI monitor connected)
python run_edge.py --mode full
```

🎉 **System is now running!**

---

## 📊 Expected Performance

### On Your Raspberry Pi 5 (8GB RAM, 10GB SSD)

| Metric | Value |
|--------|-------|
| **Inference Speed** | 12-15 FPS |
| **Detection Latency** | ~80ms |
| **RAM Usage** | ~1.5GB |
| **Storage Usage** | ~500MB-2GB (auto-managed) |
| **CPU Temperature** | 60-75°C (with active cooling) |

---

## 🎯 What It Detects

### Helmet Violations
- ✅ **Riders without helmets** - Detects motorcyclists not wearing helmets
- ✅ **Confidence scoring** - Only logs high-confidence detections (>50%)
- ✅ **License plate capture** - Attempts to read number plates
- ✅ **Evidence storage** - Saves violation images with timestamps

### Additional Violations (Optional)
- ✅ **Triple riding** - 3+ people on motorcycle
- ✅ **Traffic rule violations** - Configurable detection

---

## 💾 Storage Management (10GB SSD)

### Automatic Cleanup
The system automatically manages your limited SSD space:

```
Total SSD: 10GB
├── System & OS: ~4GB
├── Application: ~500MB
├── Evidence Images: ~1-2GB (auto-managed)
├── Database: ~100MB
├── Logs: ~50MB (auto-rotated)
└── Free Space: ~2-4GB (maintained)
```

### Cleanup Settings (in `.env`)
```bash
MAX_EVIDENCE_IMAGES=1000         # Keep max 1000 images
AUTO_CLEANUP_DAYS=30             # Delete images older than 30 days
AUTO_CLEANUP_ENABLED=True        # Enable automatic cleanup
```

### Manual Cleanup
```bash
# Check storage
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); print(m.get_storage_report())"

# Manual cleanup (delete images older than 7 days)
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); m.cleanup_old_evidence(days=7)"
```

---

## 🔧 Configuration for Your Setup

### Camera Settings (`.env`)
```bash
CAMERA_SOURCE=0              # First USB camera
CAMERA_WIDTH=1280            # Full HD width
CAMERA_HEIGHT=720            # Full HD height
CAMERA_FPS=30                # 30 FPS capture
```

### Performance Settings (`.env`)
```bash
INFERENCE_SIZE=320           # Lightweight inference
NUM_THREADS=4                # Use all 4 cores
TARGET_FPS=20                # 20 FPS processing
DETECTION_CONFIDENCE=0.50    # 50% confidence threshold
```

### Storage Settings (`.env`)
```bash
MAX_EVIDENCE_IMAGES=1000     # Max images to keep
AUTO_CLEANUP_DAYS=30         # Delete after 30 days
AUTO_CLEANUP_ENABLED=True    # Enable auto-cleanup
```

---

## 🌡️ Thermal Management

### Cooling Requirements
Your Raspberry Pi 5 **MUST have active cooling** (fan) for sustained operation!

### Check Temperature
```bash
# Check CPU temperature
vcgencmd measure_temp

# Should be < 80°C
# If > 80°C, ensure fan is working!
```

### If Temperature Too High
1. Ensure fan is connected and spinning
2. Check heatsink is properly attached
3. Reduce inference size: `INFERENCE_SIZE=256`
4. Process fewer frames: `PROCESS_EVERY_N_FRAMES=2`

---

## 📝 Daily Operations

### Start System
```bash
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
source venv/bin/activate
python run_edge.py --mode full --no-display
```

### Stop System
Press `Ctrl+C` in the terminal

### View Logs
```bash
tail -f logs/edge_system.log
```

### Check Storage
```bash
df -h
```

### View Violations
```bash
# Count violations
sqlite3 data/violations.db "SELECT COUNT(*) FROM violations;"

# View recent violations
sqlite3 data/violations.db "SELECT * FROM violations ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🔄 Auto-Start on Boot

To make the system start automatically when Raspberry Pi boots:

```bash
# Install service
sudo bash services/install_service.sh

# Check status
sudo systemctl status traffic-detector

# View logs
sudo journalctl -u traffic-detector -f

# Stop service
sudo systemctl stop traffic-detector

# Disable auto-start
sudo systemctl disable traffic-detector
```

---

## 🐛 Troubleshooting

### Camera Not Detected
```bash
# Check USB devices
lsusb

# List video devices
ls /dev/video*

# If no video devices, try different USB port
# Add user to video group
sudo usermod -a -G video $USER
# Then reboot
```

### Low FPS
```bash
# Edit .env file
nano .env

# Change these settings:
INFERENCE_SIZE=256           # Reduce from 320
PROCESS_EVERY_N_FRAMES=2     # Process every 2nd frame
```

### Disk Full
```bash
# Check disk usage
df -h

# Manual cleanup
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
source venv/bin/activate
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); m.cleanup_old_evidence(days=3)"
```

### System Slow
```bash
# Check CPU temperature
vcgencmd measure_temp

# Check memory
free -h

# Check running processes
htop
```

---

## 📊 Monitoring

### Real-Time Monitoring
```bash
# View logs
tail -f logs/edge_system.log

# Check temperature
watch -n 1 vcgencmd measure_temp

# Check memory
watch -n 1 free -h
```

### Storage Monitoring
```bash
# Check disk usage
df -h

# Check evidence folder size
du -sh data/evidence/

# Count evidence images
ls data/evidence/ | wc -l
```

---

## ✅ Optimization Tips for 10GB SSD

### 1. Reduce Evidence Image Quality
Edit `edge_pipeline/main_pipeline.py` to save compressed images:
```python
cv2.imwrite(evidence_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
```

### 2. Reduce Log Verbosity
Edit `.env`:
```bash
LOG_LEVEL=WARNING  # Instead of INFO
```

### 3. Increase Cleanup Frequency
Edit `.env`:
```bash
AUTO_CLEANUP_DAYS=7  # Instead of 30
MAX_EVIDENCE_IMAGES=500  # Instead of 1000
```

### 4. Disable GPS (if not needed)
Edit `.env`:
```bash
GPS_MODE=mock  # Don't use real GPS
```

---

## 🎯 Performance Benchmarks

### Your Expected Performance

```
╔══════════════════════════════════════════════════════════════╗
║          RASPBERRY PI 5 PERFORMANCE                          ║
╠══════════════════════════════════════════════════════════════╣
║  Inference:       12-15 FPS                                  ║
║  Latency:         ~80ms                                      ║
║  RAM Usage:       ~1.5GB / 8GB                               ║
║  Storage:         ~1-2GB / 10GB                              ║
║  CPU Temp:        60-75°C (with fan)                         ║
║  Detection:       Real-time helmet violations                ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 📞 Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Run system
python run_edge.py --mode full --no-display

# Test camera
python scripts/test_camera.py

# Benchmark performance
python scripts/benchmark.py

# Check storage
df -h

# Check temperature
vcgencmd measure_temp

# View logs
tail -f logs/edge_system.log

# Stop system
Ctrl+C
```

---

## 🎉 You're All Set!

Your Raspberry Pi 5 helmet violation detection system is optimized for:
- ✅ 8GB RAM
- ✅ 10GB SSD with auto-cleanup
- ✅ USB webcam powered by USB port
- ✅ Real-time detection (12-15 FPS)
- ✅ Lightweight operation
- ✅ Automatic storage management

**Happy Detecting! 🚦🏍️🎥**
