# ⚡ Quick Start Guide

Get your Raspberry Pi 5 traffic violation detection system running in 15 minutes!

---

## 🎯 Prerequisites

- ✅ Raspberry Pi 5 with Raspberry Pi OS (64-bit) installed
- ✅ USB Webcam connected
- ✅ Internet connection
- ✅ SSH access enabled

---

## 🚀 5-Step Quick Start

### Step 1: Transfer Files (2 minutes)

**From your Windows PC:**

```bash
# Copy entire project folder to Raspberry Pi
scp -r "Embedded AI-Based Traffic Violation Detection System" pi@raspberrypi.local:~/
```

### Step 2: Run Setup (15 minutes)

**On Raspberry Pi:**

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Navigate to project
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/

# Run setup script
chmod +x setup_rpi5.sh
./setup_rpi5.sh
```

☕ **Grab a coffee!** Setup takes ~15 minutes.

### Step 3: Copy Models (1 minute)

**From your Windows PC:**

```bash
# Copy main detection model
scp backend/yolov8n.pt pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/best.pt
```

### Step 4: Test Camera (30 seconds)

**On Raspberry Pi:**

```bash
# Activate environment
source venv/bin/activate

# Test camera
python scripts/test_camera.py
```

Press 'q' to quit when you see the camera feed.

### Step 5: Run System (Ready!)

**On Raspberry Pi:**

```bash
# Run full system (with display)
python run_edge.py --mode full

# Or headless (no display)
python run_edge.py --mode full --no-display
```

---

## 🎉 That's It!

Your system is now running and detecting traffic violations in real-time!

---

## 📊 Quick Commands

```bash
# Activate environment (always run this first)
source venv/bin/activate

# Test camera
python scripts/test_camera.py

# Run benchmark
python scripts/benchmark.py

# Run full system with display
python run_edge.py --mode full

# Run headless (no monitor)
python run_edge.py --mode full --no-display

# Test with video file
python run_edge.py --mode full --video /path/to/video.mp4

# View logs
tail -f logs/edge_system.log
```

---

## 🔧 Troubleshooting

### Camera not working?
```bash
# Check connected cameras
v4l2-ctl --list-devices

# Try different camera source
python run_edge.py --source 1
```

### Low FPS?
Edit `.env` file:
```bash
INFERENCE_SIZE=256           # Reduce from 320
PROCESS_EVERY_N_FRAMES=2     # Process every 2nd frame
```

### System too hot?
```bash
# Check temperature
vcgencmd measure_temp

# Should be < 80°C. If higher, ensure fan is working!
```

---

## 📖 Full Documentation

For detailed setup, optimization, and troubleshooting:
- **Full Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Main README:** `README.md`

---

## 🆘 Need Help?

1. Check logs: `tail -f logs/edge_system.log`
2. Review `DEPLOYMENT_GUIDE.md` for detailed troubleshooting
3. Verify hardware connections and cooling

---

**Happy Detecting! 🚦🎥**
