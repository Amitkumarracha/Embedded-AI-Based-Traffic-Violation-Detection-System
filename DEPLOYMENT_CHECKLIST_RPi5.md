# 🚀 Deployment Checklist - Raspberry Pi 5 (8GB RAM, 10GB SSD)

## Pre-Deployment Verification ✅

### Hardware Requirements
- [ ] **Raspberry Pi 5** with **8GB RAM** ✅
- [ ] **10GB SSD** (or microSD) formatted and ready ✅
- [ ] **USB Webcam** (UVC compatible, USB-powered) ✅
- [ ] **Active Cooling** (fan + heatsink) - **MANDATORY** ⚠️
- [ ] **27W USB-C Power Supply** (5V/5A official RPi PSU)
- [ ] **Optional:** USB GPS Module (VK-162 or similar)
- [ ] **Optional:** HDMI monitor for initial setup

### Software Requirements
- [ ] **Raspberry Pi OS 64-bit** (Bookworm or later)
- [ ] **SSH enabled** for remote access
- [ ] **Internet connection** for initial setup
- [ ] **Git installed** (usually pre-installed)

---

## Step 1: Prepare Raspberry Pi (30 minutes)

### 1.1 Flash OS
```bash
# Use Raspberry Pi Imager on Windows PC
# Select: Raspberry Pi OS (64-bit) - Bookworm
# Configure:
#   - Hostname: raspberrypi
#   - Enable SSH
#   - Set username: pi
#   - Set password: [your password]
#   - Configure WiFi (optional)
```

- [ ] OS flashed to SD card/SSD
- [ ] First boot completed
- [ ] SSH access verified

### 1.2 Initial System Setup
```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git python3-pip python3-venv

# Enable camera (if using CSI camera)
sudo raspi-config
# Interface Options → Camera → Enable

# Reboot
sudo reboot
```

- [ ] System updated
- [ ] Essential tools installed
- [ ] Camera enabled (if needed)

---

## Step 2: Transfer System Files (10 minutes)

### 2.1 From Windows PC

**Option A: Using SCP (Git Bash or PowerShell)**
```bash
# From Windows PC
cd "E:\traffic violation detection system"
scp -r "Embedded AI-Based Traffic Violation Detection System" pi@raspberrypi.local:~/
```

**Option B: Using WinSCP**
1. Connect to `raspberrypi.local`
2. Navigate to `/home/pi/`
3. Drag and drop entire folder

**Option C: Using USB Drive**
1. Copy folder to USB drive
2. Insert USB into Raspberry Pi
3. Mount and copy:
```bash
sudo mount /dev/sda1 /mnt
cp -r /mnt/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System ~/
sudo umount /mnt
```

- [ ] System files transferred
- [ ] Folder structure intact
- [ ] Models included (check `models/` directory)

---

## Step 3: Run Setup Script (20 minutes)

### 3.1 Execute Setup
```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Navigate to project
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/

# Make setup script executable
chmod +x setup_rpi5.sh

# Run setup (takes 15-20 minutes)
./setup_rpi5.sh
```

**What the script does:**
- Creates Python virtual environment
- Installs all dependencies
- Configures system settings
- Creates necessary directories
- Sets up logging

- [ ] Setup script completed successfully
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] No error messages

### 3.2 Verify Installation
```bash
# Activate virtual environment
source venv/bin/activate

# Check Python version
python --version  # Should be 3.11+

# Check key packages
pip list | grep -E "ultralytics|opencv|torch"

# Test imports
python -c "import cv2, torch, ultralytics; print('✅ All imports successful')"
```

- [ ] Python 3.11+ installed
- [ ] Key packages present
- [ ] Imports working

---

## Step 4: Configure System (10 minutes)

### 4.1 Review Configuration
```bash
# Edit configuration file
nano .env.rpi
```

**Key Settings to Verify:**
```bash
# Device
DEVICE=cpu
INFERENCE_SIZE=320              # Balanced for 8GB RAM
NUM_THREADS=4                   # Use all 4 cores
TARGET_FPS=20

# Camera
CAMERA_SOURCE=0                 # First USB camera
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=30

# Storage (CRITICAL for 10GB SSD)
MAX_EVIDENCE_IMAGES=1000        # Auto-delete oldest
AUTO_CLEANUP_DAYS=30            # Keep 30 days
AUTO_CLEANUP_ENABLED=True       # MUST be True

# Display
SHOW_DISPLAY=False              # Headless mode

# Speed Detection
PIXELS_PER_METER=8.0            # Adjust after calibration
SPEED_LIMIT_KMH=60.0
```

- [ ] Configuration reviewed
- [ ] Storage settings verified (10GB SSD)
- [ ] Camera source correct
- [ ] Auto-cleanup enabled

### 4.2 Verify Models
```bash
# Check models directory
ls -lh models/

# Should see:
# best.pt (6.23 MB)
# yolo11nHelmet_Detection_using_Yolo11.pt (6.51 MB)
# speed_detection.pt (optional)
```

- [ ] Models present in `models/` directory
- [ ] File sizes correct
- [ ] No corrupted files

---

## Step 5: Test Components (15 minutes)

### 5.1 Test Camera
```bash
# Activate environment
source venv/bin/activate

# Test camera
python scripts/test_camera.py

# Should see:
# ✓ Camera opened successfully
# Camera FPS: ~30
# Press 'q' to quit
```

- [ ] Camera detected
- [ ] Video feed working
- [ ] FPS stable (~30)

### 5.2 Test Detection
```bash
# Run benchmark
python run_edge.py --mode benchmark

# Should see:
# Mean: 50-80 ms/frame
# FPS: 15-20
```

- [ ] Detection working
- [ ] FPS acceptable (15-20)
- [ ] No errors

### 5.3 Test Storage Manager
```bash
# Test storage management
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); print(m.get_storage_report())"

# Should see:
# Total Disk: ~10 GB
# Free: ~8 GB
# Evidence Images: 0 MB
```

- [ ] Storage manager working
- [ ] Disk space reported correctly
- [ ] Auto-cleanup ready

---

## Step 6: Deploy System (5 minutes)

### 6.1 Start System
```bash
# Activate environment
source venv/bin/activate

# Start full system (headless mode)
python run_edge.py --mode full --no-display

# Should see:
# ✓ Camera started
# ✓ Detector initialized
# ✓ Tracker initialized
# ✓ Speed Detector initialized
# ✓ Violation Gate initialized
# All threads started. Running pipeline...
```

- [ ] System started successfully
- [ ] All components initialized
- [ ] No error messages
- [ ] Processing frames

### 6.2 Monitor System
```bash
# In another SSH session
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/

# Watch logs
tail -f logs/edge_system.log

# Check temperature
watch -n 5 vcgencmd measure_temp

# Check storage
watch -n 60 df -h
```

- [ ] Logs updating
- [ ] Temperature stable (<80°C)
- [ ] Storage not filling up

---

## Step 7: Validation Tests (30 minutes)

### 7.1 Run for 30 Minutes
```bash
# Let system run for 30 minutes
# Monitor:
# - Temperature (should stay <80°C)
# - RAM usage (should stay <2GB)
# - Storage (should not grow rapidly)
# - FPS (should stay 15-20)
```

- [ ] System stable for 30 minutes
- [ ] Temperature acceptable
- [ ] RAM usage normal
- [ ] Storage managed

### 7.2 Test Violation Detection
```bash
# Present test scenarios to camera:
# 1. Person without helmet
# 2. Multiple persons on motorcycle
# 3. Vehicle with visible plate

# Check database
sqlite3 data/violations.db "SELECT COUNT(*) FROM violations;"

# Check evidence images
ls -lh data/evidence/
```

- [ ] Violations detected
- [ ] Database updated
- [ ] Evidence images saved

### 7.3 Test Auto-Cleanup
```bash
# Force cleanup test
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); m.check_and_cleanup(); print(m.get_storage_report())"
```

- [ ] Cleanup executed
- [ ] Old files removed (if any)
- [ ] Storage report accurate

---

## Step 8: Production Setup (Optional)

### 8.1 Install as System Service
```bash
# Install systemd service
cd services/
chmod +x install_service.sh
sudo ./install_service.sh

# Enable auto-start on boot
sudo systemctl enable traffic-detector.service

# Start service
sudo systemctl start traffic-detector.service

# Check status
sudo systemctl status traffic-detector.service
```

- [ ] Service installed
- [ ] Auto-start enabled
- [ ] Service running

### 8.2 Configure Remote Access (Optional)
```bash
# Access dashboard from another device
# http://raspberrypi.local:8000

# Or use IP address
hostname -I
# http://[IP_ADDRESS]:8000
```

- [ ] Dashboard accessible
- [ ] API responding
- [ ] WebSocket working

---

## Final Verification Checklist ✅

### Hardware
- [ ] Raspberry Pi 5 (8GB RAM) running
- [ ] 10GB SSD with auto-cleanup enabled
- [ ] USB webcam connected and working
- [ ] Active cooling (fan) running
- [ ] Temperature stable (<80°C)
- [ ] Power supply adequate (27W)

### Software
- [ ] Raspberry Pi OS 64-bit installed
- [ ] System files transferred
- [ ] Setup completed successfully
- [ ] Configuration optimized for 10GB SSD
- [ ] All dependencies installed

### System Components
- [ ] Camera capture working (30 FPS)
- [ ] Detection running (15-20 FPS)
- [ ] Tracking functional
- [ ] Speed detection active
- [ ] Violation gate filtering
- [ ] OCR working (if plates visible)
- [ ] GPS logging (real or mock)
- [ ] Database writing
- [ ] Storage auto-cleanup enabled

### Performance
- [ ] FPS: 15-20 (acceptable)
- [ ] RAM: <2GB (within limits)
- [ ] Storage: <2GB (managed)
- [ ] CPU: 40-60% (normal)
- [ ] Temperature: <80°C (safe)
- [ ] Latency: <100ms (good)

### Validation
- [ ] System runs for 30+ minutes
- [ ] Violations detected correctly
- [ ] Evidence saved properly
- [ ] Database updated
- [ ] Auto-cleanup working
- [ ] No memory leaks
- [ ] No storage issues
- [ ] No thermal throttling

---

## Troubleshooting Guide

### Issue: Camera Not Detected
```bash
# Check USB devices
lsusb

# List video devices
ls /dev/video*

# Try different USB port
# Update CAMERA_SOURCE in .env.rpi
```

### Issue: Low FPS (<10)
```bash
# Reduce inference size
nano .env.rpi
# Change: INFERENCE_SIZE=256

# Process every 2nd frame
# Change: PROCESS_EVERY_N_FRAMES=2
```

### Issue: High Temperature (>80°C)
```bash
# Check fan
# Ensure heatsink attached
# Reduce inference size
# Add better cooling
```

### Issue: Disk Full
```bash
# Manual cleanup
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); m.cleanup_old_evidence(days=3)"

# Reduce retention
nano .env.rpi
# Change: AUTO_CLEANUP_DAYS=7
# Change: MAX_EVIDENCE_IMAGES=500
```

### Issue: Out of Memory
```bash
# Reduce inference size
nano .env.rpi
# Change: INFERENCE_SIZE=256

# Process fewer frames
# Change: PROCESS_EVERY_N_FRAMES=2
```

---

## Post-Deployment Monitoring

### Daily Checks
```bash
# Check system status
systemctl status traffic-detector.service

# Check logs
tail -n 50 logs/edge_system.log

# Check temperature
vcgencmd measure_temp

# Check storage
df -h

# Check violations
sqlite3 data/violations.db "SELECT COUNT(*) FROM violations WHERE date(timestamp) = date('now');"
```

### Weekly Maintenance
```bash
# Review storage usage
python -c "from edge_core.storage_manager import StorageManager; m = StorageManager(); print(m.get_storage_report())"

# Check for updates
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
git pull  # If using git

# Backup database
cp data/violations.db data/violations_backup_$(date +%Y%m%d).db
```

---

## Success Criteria ✅

Your deployment is successful if:

✅ **System runs continuously** for 1+ hour without crashes  
✅ **FPS stable** at 15-20 frames/second  
✅ **RAM usage** stays below 2GB  
✅ **Storage** stays below 2GB (auto-cleanup working)  
✅ **Temperature** stays below 80°C  
✅ **Violations detected** and logged correctly  
✅ **Evidence saved** with images and GPS  
✅ **No errors** in logs  

---

## Deployment Complete! 🎉

Your **Embedded AI-Based Traffic Violation Detection System** is now:

✅ **Deployed** on Raspberry Pi 5  
✅ **Optimized** for 8GB RAM + 10GB SSD  
✅ **Running** with auto-cleanup enabled  
✅ **Detecting** helmet violations in real-time  
✅ **Logging** violations with evidence  
✅ **Managed** with automatic storage cleanup  

**Status:** 🟢 **OPERATIONAL**

---

**Deployment Date:** _______________  
**Deployed By:** _______________  
**Location:** _______________  
**Notes:** _______________

---

**For support, refer to:**
- `START_HERE.md` - Quick start guide
- `RASPBERRY_PI_SETUP.md` - Detailed setup
- `SYSTEM_VALIDATION_COMPLETE.md` - System validation
- `logs/edge_system.log` - System logs

**Happy Detecting! 🚦🏍️🎥**
