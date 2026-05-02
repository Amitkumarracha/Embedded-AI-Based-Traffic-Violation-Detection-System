# Traffic Violation Detection System - Web Interface Guide

## 🎉 Web Interface is Now Running!

Your Traffic Violation Detection System web interface is successfully running at:

**http://127.0.0.1:8080**

## 🚀 Quick Start

### Access the Web Interface

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Navigate to: **http://127.0.0.1:8080**
3. You should see the modern dashboard interface

### Starting Detection

1. Click the **"▶️ Start"** button in the Live Detection Feed section
2. The system will initialize the camera and start detecting violations
3. Real-time video feed will appear in the main window
4. Violations will be logged in the "Recent Violations" panel

### Stopping Detection

1. Click the **"⏹️ Stop"** button to stop the detection system
2. The video feed will pause

## 📊 Dashboard Features

### 1. Statistics Cards
- **Total Violations**: Cumulative count of all detected violations
- **Today's Violations**: Violations detected today
- **Active Detections**: Current number of objects being tracked
- **System Uptime**: How long the system has been running

### 2. Live Detection Feed
- Real-time video stream with bounding boxes
- FPS counter showing performance
- Controls for Start/Stop/Capture
- Screenshot capture functionality

### 3. Recent Violations Panel
- Live list of detected violations
- Timestamp for each violation
- Violation type (No Helmet, Speeding, etc.)
- License plate information (if detected)
- Export functionality to CSV

### 4. System Settings
- **Detection Confidence Threshold**: Adjust sensitivity (0.1 - 1.0)
- **Speed Limit**: Set the speed limit in km/h
- **Process Every N Frames**: Control processing frequency for performance
- Save button to apply changes

### 5. System Logs
- Real-time system messages
- Color-coded by severity (Info, Warning, Error)
- Clear button to reset logs
- Auto-scrolling to latest messages

## 🎮 Controls & Actions

### Main Controls

| Button | Action | Description |
|--------|--------|-------------|
| ▶️ Start | Start Detection | Begins camera capture and violation detection |
| ⏹️ Stop | Stop Detection | Pauses the detection system |
| 📸 Capture | Screenshot | Saves current frame as image |
| 📥 Export | Export Data | Downloads violations as CSV file |
| 💾 Save Settings | Apply Settings | Saves configuration changes |

### Keyboard Shortcuts

- **Ctrl + S**: Save settings
- **Ctrl + E**: Export violations
- **Ctrl + C**: Stop server (in terminal)

## ⚙️ Configuration

### Adjusting Detection Sensitivity

1. Locate the "Detection Confidence Threshold" slider
2. Move left for more detections (less strict)
3. Move right for fewer detections (more strict)
4. Click "Save Settings" to apply

### Performance Optimization

**For Low-End Systems:**
- Set "Process Every N Frames" to 2 or 3
- Lower confidence threshold to 0.3-0.4
- Close other applications

**For High-End Systems:**
- Set "Process Every N Frames" to 1
- Higher confidence threshold (0.6-0.7)
- Enable GPU in .env file (if available)

## 📱 Features

### Real-Time Monitoring
- Live video feed with object detection
- Instant violation alerts
- WebSocket-based communication for low latency

### Data Management
- Automatic violation logging to database
- Export violations to CSV format
- Evidence image storage
- Historical data tracking

### Notifications
- Browser notifications for new violations (if permitted)
- Visual alerts in the interface
- System log messages

## 🔧 Troubleshooting

### Issue: "Cannot connect to server"

**Solution:**
- Ensure the web server is running
- Check terminal for error messages
- Verify port 8080 is not blocked by firewall
- Try accessing http://localhost:8080 instead

### Issue: "No video feed"

**Solution:**
- Click the "Start" button
- Check if camera is connected and working
- Verify camera permissions in Windows settings
- Try different camera source in .env file

### Issue: "Slow performance"

**Solution:**
- Increase "Process Every N Frames" value
- Close other applications
- Reduce browser zoom level
- Check CPU usage in Task Manager

### Issue: "Violations not being detected"

**Solution:**
- Lower the confidence threshold
- Ensure proper lighting in camera view
- Check if objects are clearly visible
- Verify model files are present in models/ folder

## 🌐 Network Access

### Local Access Only (Default)
- URL: http://127.0.0.1:8080
- Only accessible from this computer

### Network Access (Optional)
To access from other devices on your network:

1. Stop the server (Ctrl+C in terminal)
2. Run with network binding:
   ```bash
   python web_server.py --host 0.0.0.0 --port 8080
   ```
3. Find your computer's IP address:
   ```bash
   ipconfig
   ```
4. Access from other devices: http://YOUR_IP:8080

**Security Warning:** Only enable network access on trusted networks!

## 📊 Data Export

### Exporting Violations

1. Click the "📥 Export" button in Recent Violations section
2. CSV file will download automatically
3. Open with Excel, Google Sheets, or any CSV viewer

### CSV Format
```
ID,Type,Timestamp,Confidence,License Plate
1,No Helmet,2026-04-30 14:30:15,0.85,ABC123
2,Speeding,2026-04-30 14:31:22,0.92,XYZ789
```

## 🎨 Interface Customization

The interface uses a modern dark theme optimized for:
- Long monitoring sessions
- Reduced eye strain
- Clear visibility of alerts
- Professional appearance

## 📈 Performance Metrics

### Expected Performance

| System Type | FPS | Latency | Detections/sec |
|-------------|-----|---------|----------------|
| Low-end CPU | 5-10 | 200ms | 5-10 |
| Mid-range CPU | 15-20 | 100ms | 15-20 |
| High-end CPU | 25-30 | 50ms | 25-30 |
| With GPU | 30+ | <30ms | 30+ |

## 🔐 Security Notes

- Web interface runs locally by default
- No external internet connection required
- All data stored locally in SQLite database
- Evidence images saved in local evidence/ folder

## 📝 System Requirements

### Minimum
- Windows 10/11
- 4GB RAM
- Dual-core CPU
- Webcam or video input
- Modern web browser

### Recommended
- Windows 10/11
- 8GB+ RAM
- Quad-core CPU
- HD Webcam
- Chrome/Firefox/Edge (latest version)

## 🆘 Support

### Getting Help

1. Check the logs in the System Logs panel
2. Review terminal output for error messages
3. Verify all dependencies are installed
4. Ensure model files are present

### Common Commands

**Start Web Server:**
```bash
python web_server.py --host 127.0.0.1 --port 8080
```

**Check Server Status:**
- Look for "Uvicorn running on..." message in terminal

**Stop Server:**
- Press Ctrl+C in the terminal

## 🎯 Next Steps

1. **Test the System**: Click Start and verify camera feed
2. **Adjust Settings**: Fine-tune detection parameters
3. **Monitor Violations**: Watch the Recent Violations panel
4. **Export Data**: Download violation reports
5. **Optimize Performance**: Adjust settings for your hardware

## 📚 Additional Resources

- **Main Documentation**: See README.md
- **Windows Setup**: See WINDOWS_SETUP_GUIDE.md
- **Speed Detection**: See SPEED_DETECTION_GUIDE.md
- **Deployment**: See DEPLOYMENT_GUIDE.md

---

**Enjoy monitoring traffic violations with your AI-powered system!** 🚦🤖
