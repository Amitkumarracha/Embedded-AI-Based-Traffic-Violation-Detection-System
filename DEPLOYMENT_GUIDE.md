# 🚀 Raspberry Pi 5 Deployment Guide

Complete step-by-step guide to deploy the Traffic Violation Detection System on Raspberry Pi 5.

---

## 📋 Prerequisites

### Hardware
- ✅ Raspberry Pi 5 (8GB recommended, 4GB minimum)
- ✅ 64GB+ microSD card (Class 10/U3) or NVMe SSD
- ✅ USB Webcam (UVC compatible, e.g., Logitech C920/C270)
- ✅ 27W USB-C Power Supply (official Raspberry Pi 5 PSU)
- ✅ Active cooling (heatsink + fan required for sustained AI inference)
- ✅ Optional: USB GPS module (VK-162 G-Mouse or similar)

### Software
- Raspberry Pi OS (64-bit) Bookworm - Desktop or Lite
- Internet connection for initial setup

---

## 🔧 Step 1: Prepare Raspberry Pi

### 1.1 Flash Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash **Raspberry Pi OS (64-bit) Bookworm** to microSD card
3. Configure WiFi and SSH in advanced settings
4. Insert card and boot Raspberry Pi

### 1.2 Initial System Setup

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Enable camera and increase GPU memory
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Navigate to: Performance Options → GPU Memory → 256

# Reboot
sudo reboot
```

---

## 📦 Step 2: Transfer Project Files

### Option A: From Windows PC via SCP

```bash
# On Windows PC (PowerShell or Git Bash):
scp -r "Embedded AI-Based Traffic Violation Detection System" pi@raspberrypi.local:~/
```

### Option B: From USB Drive

```bash
# On Raspberry Pi:
# Insert USB drive, then:
sudo mkdir /mnt/usb
sudo mount /dev/sda1 /mnt/usb
cp -r /mnt/usb/"Embedded AI-Based Traffic Violation Detection System" ~/
sudo umount /mnt/usb
```

### Option C: Git Clone (if project is in repository)

```bash
# On Raspberry Pi:
cd ~
git clone <your-repo-url>
cd "Embedded AI-Based Traffic Violation Detection System"
```

---

## 🛠️ Step 3: Run Setup Script

```bash
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/

# Make setup script executable
chmod +x setup_rpi5.sh

# Run setup (takes 15-20 minutes)
./setup_rpi5.sh
```

The setup script will:
- ✅ Install system dependencies (OpenCV, V4L2, GPS, etc.)
- ✅ Create Python virtual environment
- ✅ Install PyTorch (ARM64 CPU version)
- ✅ Install project dependencies
- ✅ Configure camera and GPU memory
- ✅ Create data directories

---

## 📥 Step 4: Copy Model Weights

### From Windows PC

```bash
# Copy main detection model
scp backend/yolov8n.pt pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/best.pt

# Copy ONNX model (if available - recommended for better performance)
scp backend/best.onnx pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/best.onnx

# Copy helmet detection model (optional)
scp backend/yolov8n-pose.pt pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/yolo11nHelmet_Detection_using_Yolo11.pt
```

### Verify Models

```bash
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
ls -lh models/

# Should see:
# best.pt or best.onnx (required)
# yolo11nHelmet_Detection_using_Yolo11.pt (optional)
```

---

## 🎥 Step 5: Test USB Camera

```bash
# Activate virtual environment
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
source venv/bin/activate

# Check connected cameras
v4l2-ctl --list-devices

# Test camera (should show live feed)
python scripts/test_camera.py

# Test with second camera (if you have multiple)
python scripts/test_camera.py 1
```

**Troubleshooting:**
- No camera detected? Check USB connection and run `lsusb`
- Permission denied? Run `sudo usermod -a -G video $USER` and reboot
- Black screen? Try different USB port or camera

---

## ⚡ Step 6: Run Performance Benchmark

```bash
# Still in virtual environment
python scripts/benchmark.py
```

Expected results on Raspberry Pi 5:
- **FP32 @ 320px:** 8-12 FPS
- **ONNX @ 320px:** 12-15 FPS
- **INT8 @ 320px:** 15-25 FPS (if quantized model available)

If FPS < 10, consider:
- Using ONNX model instead of PyTorch
- Reducing inference size to 256×256
- Processing every 2nd frame

---

## 🚀 Step 7: Run Full System

### With Display (HDMI monitor connected)

```bash
# Activate environment
source venv/bin/activate

# Run full system
python run_edge.py --mode full

# Or with specific camera
python run_edge.py --mode full --source 1
```

### Headless Mode (No monitor)

```bash
# Run without display
python run_edge.py --mode full --no-display

# System will run in background
# Access logs: tail -f logs/edge_system.log
```

### Test with Video File

```bash
# Test with video instead of camera
python run_edge.py --mode full --video /path/to/test_video.mp4
```

---

## 🔄 Step 8: Auto-Start on Boot (Optional)

To make the system start automatically when Raspberry Pi boots:

```bash
# Install systemd service
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
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

## 📊 Step 9: Access Dashboard (Optional)

If you want to access the web dashboard:

```bash
# The system runs a FastAPI server on port 8000
# Access from browser:
http://raspberrypi.local:8000

# Or use IP address:
http://192.168.1.XXX:8000
```

Dashboard features:
- 📹 Live camera feed
- 📋 Violation history
- 📈 Statistics and analytics
- 🗺️ GPS location map

---

## 🔍 Monitoring & Troubleshooting

### Check System Resources

```bash
# CPU temperature (should be < 80°C)
vcgencmd measure_temp

# CPU usage
htop

# Memory usage
free -h

# Disk space
df -h
```

### View Logs

```bash
# Application logs
tail -f logs/edge_system.log

# System logs (if running as service)
sudo journalctl -u traffic-detector -f
```

### Common Issues

#### 1. High CPU Temperature (> 80°C)
**Solution:**
- Ensure active cooling (fan) is working
- Reduce inference size: Edit `.env` → `INFERENCE_SIZE=256`
- Process fewer frames: Edit `.env` → `PROCESS_EVERY_N_FRAMES=2`

#### 2. Out of Memory
**Solution:**
- Close other applications
- Use ONNX model instead of PyTorch
- Increase swap: `sudo dphys-swapfile swapoff && sudo nano /etc/dphys-swapfile` (set CONF_SWAPSIZE=2048)

#### 3. Low FPS (< 10)
**Solution:**
- Use ONNX model
- Reduce inference size to 256×256
- Process every 2nd or 3rd frame
- Check CPU temperature

#### 4. Camera Not Detected
**Solution:**
- Check USB connection: `lsusb`
- List video devices: `ls /dev/video*`
- Add user to video group: `sudo usermod -a -G video $USER`
- Reboot

#### 5. GPS Not Working
**Solution:**
- Check GPS module connection: `lsusb`
- Install gpsd: `sudo apt install gpsd gpsd-clients`
- Test GPS: `cgps -s`
- System will use mock GPS if real GPS unavailable

---

## 🎯 Performance Optimization

### 1. Use ONNX Model
```bash
# Convert PyTorch to ONNX (on development machine)
python scripts/export_onnx.py --model models/best.pt --output models/best.onnx

# Copy to Raspberry Pi
scp models/best.onnx pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/
```

### 2. Adjust Inference Size
Edit `.env` file:
```bash
INFERENCE_SIZE=256  # Reduce from 320 for faster inference
```

### 3. Process Fewer Frames
Edit `.env` file:
```bash
PROCESS_EVERY_N_FRAMES=2  # Process every 2nd frame
```

### 4. Disable Display
```bash
# Run headless for better performance
python run_edge.py --mode full --no-display
```

---

## 📝 Configuration

All settings are in `.env` file. Key parameters:

```bash
# Camera
CAMERA_SOURCE=0              # 0=first USB camera, 1=second
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=30

# Inference
INFERENCE_SIZE=320           # 256, 320, 416, 640
NUM_THREADS=4                # CPU threads for inference
TARGET_FPS=15                # Target processing FPS

# Detection
DETECTION_CONFIDENCE=0.50    # Confidence threshold
PROCESS_EVERY_N_FRAMES=1     # Process every Nth frame

# Display
SHOW_DISPLAY=False           # True for HDMI display, False for headless

# GPS
GPS_MODE=real                # 'real' for USB GPS, 'mock' for development
```

---

## 🔐 Security Considerations

1. **Change default password:**
   ```bash
   passwd
   ```

2. **Enable firewall:**
   ```bash
   sudo apt install ufw
   sudo ufw allow 22    # SSH
   sudo ufw allow 8000  # Dashboard (if needed)
   sudo ufw enable
   ```

3. **Disable SSH password authentication (use keys):**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```

4. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f logs/edge_system.log`
2. Review troubleshooting section above
3. Check main project documentation in `docs/` directory
4. Verify hardware connections and cooling

---

## ✅ Deployment Checklist

- [ ] Raspberry Pi 5 with 64-bit OS installed
- [ ] Active cooling (fan) installed and working
- [ ] USB webcam connected and tested
- [ ] Project files transferred to Raspberry Pi
- [ ] Setup script completed successfully
- [ ] Model weights copied to `models/` directory
- [ ] Camera test passed
- [ ] Performance benchmark completed (FPS ≥ 10)
- [ ] Full system tested and working
- [ ] (Optional) Auto-start service configured
- [ ] (Optional) GPS module connected and tested

---

**🎉 Congratulations! Your edge AI traffic violation detection system is now deployed and running on Raspberry Pi 5!**
