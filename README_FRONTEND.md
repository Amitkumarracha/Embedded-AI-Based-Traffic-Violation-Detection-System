# 🚦 Traffic Violation Detection System - Web Frontend

## 🎉 New Feature: Modern Web Interface!

This project now includes a **professional web-based frontend** with real-time monitoring capabilities!

---

## 🌟 Features

### 📊 Real-Time Dashboard
- Live statistics (Total Violations, Today's Count, Active Detections, System Uptime)
- Modern dark theme optimized for long monitoring sessions
- Responsive design that works on all screen sizes
- Color-coded alerts and notifications

### 🎥 Live Video Feed
- Real-time camera stream with object detection overlays
- Bounding boxes around detected objects
- Confidence scores and labels
- FPS counter for performance monitoring
- Screenshot capture functionality

### 🚨 Violation Monitoring
- Real-time violation alerts
- Detailed violation information (type, timestamp, license plate)
- Historical violation list
- CSV export for data analysis
- Browser notifications (optional)

### ⚙️ System Controls
- Start/Stop detection with one click
- Adjustable detection confidence threshold
- Configurable speed limits
- Frame processing rate control
- Settings persistence

### 📋 System Logs
- Real-time system messages
- Color-coded by severity (Info, Warning, Error)
- Auto-scrolling to latest messages
- Clear log functionality

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Run the Windows setup script
setup_windows.bat
```

This will:
- Create a virtual environment
- Install all required Python packages
- Set up necessary directories

### 2. Start the Web Server

**Option A: Quick Launcher (Recommended)**
```bash
# Double-click this file
START_WEB_INTERFACE.bat
```

**Option B: Manual Start**
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Start the web server
python web_server.py --host 127.0.0.1 --port 8080
```

### 3. Access the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:8080
```

### 4. Start Detection

1. Click the **"▶️ Start"** button
2. Allow camera access if prompted
3. Watch violations appear in real-time!

---

## 📁 Project Structure

```
Embedded-AI-Based-Traffic-Violation-Detection-System/
├── web_frontend/                    # Frontend files
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # Modern UI styling
│   │   ├── js/
│   │   │   └── app.js              # Frontend logic & WebSocket
│   │   └── images/
│   │       └── placeholder.jpg      # Video placeholder
│   └── templates/
│       └── index.html              # Main dashboard page
│
├── web_server.py                   # FastAPI backend server
├── edge_core/                      # Detection modules
├── edge_database/                  # Database operations
├── edge_pipeline/                  # Processing pipeline
├── models/                         # YOLO models
│
├── START_WEB_INTERFACE.bat        # Quick launcher
├── setup_windows.bat              # Windows setup script
├── requirements_windows.txt       # Python dependencies
│
└── Documentation/
    ├── WEB_INTERFACE_GUIDE.md     # Detailed user guide
    ├── FRONTEND_SUMMARY.md        # Feature overview
    └── WINDOWS_SETUP_GUIDE.md     # Installation guide
```

---

## 🎮 User Interface

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  🚦 Traffic Violation Detection System                  │
│                                          🟢 System Active │
├─────────────────────────────────────────────────────────┤
│  📊 Stats    📅 Today    🎯 Active    ⏱️ Uptime        │
│    125         12          3          2h 15m            │
├──────────────────────────────┬──────────────────────────┤
│  🎥 Live Detection Feed      │  🚨 Recent Violations    │
│  ┌────────────────────────┐  │  ┌────────────────────┐ │
│  │                        │  │  │ No Helmet          │ │
│  │   [Video Stream]       │  │  │ 14:30:15           │ │
│  │                        │  │  │ ABC123             │ │
│  │                        │  │  ├────────────────────┤ │
│  └────────────────────────┘  │  │ Speeding           │ │
│  ▶️ Start  ⏹️ Stop  📸 Capture │  │ 14:28:42           │ │
│                              │  │ XYZ789             │ │
├──────────────────────────────┼──────────────────────────┤
│  ⚙️ System Settings          │  📋 System Logs          │
│  Confidence: [====|----] 0.5 │  [14:30] Detection start │
│  Speed Limit: 60 km/h        │  [14:29] Camera opened   │
│  Process Frames: 1           │  [14:28] System ready    │
│  💾 Save Settings            │  🗑️ Clear Logs           │
└──────────────────────────────┴──────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Device Configuration
DEVICE=cpu                    # Use 'cuda' for GPU
INFERENCE_SIZE=640           # Detection resolution
NUM_THREADS=4                # CPU threads

# Camera Settings
CAMERA_SOURCE=0              # 0=default webcam, 1=external
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720

# Detection Settings
DETECTION_CONFIDENCE=0.50    # Confidence threshold
SPEED_LIMIT_KMH=60.0        # Speed limit
PROCESS_EVERY_N_FRAMES=1    # Frame skip for performance

# Display
SHOW_DISPLAY=True           # Show detection window
```

### Web Server Settings

```bash
# Default settings
HOST=127.0.0.1              # Localhost only
PORT=8080                   # Web server port

# For network access (use with caution)
HOST=0.0.0.0                # Allow network connections
PORT=8080
```

---

## 📊 API Endpoints

### REST API

```
GET  /                      # Main dashboard
GET  /api/stats            # System statistics
GET  /api/violations/recent # Recent violations
GET  /api/violations/export # Export to CSV
```

### WebSocket

```
WS   /ws                    # Real-time updates
```

**WebSocket Messages:**
- `violation`: New violation detected
- `stats`: Statistics update
- `frame`: Video frame update
- `log`: System log message

---

## 🎯 Usage Examples

### Starting Detection

```javascript
// Frontend automatically connects via WebSocket
// Click "Start" button or send command:
{
  "type": "command",
  "command": "start"
}
```

### Adjusting Settings

```javascript
// Update detection settings
{
  "type": "command",
  "command": "update_settings",
  "data": {
    "confidence": 0.6,
    "speedLimit": 80,
    "processFrames": 2
  }
}
```

### Exporting Data

```bash
# Download violations as CSV
curl http://127.0.0.1:8080/api/violations/export -o violations.csv
```

---

## 🔐 Security

### Local Access (Default)
- Server binds to `127.0.0.1` (localhost only)
- Only accessible from the same computer
- No external network exposure

### Network Access (Optional)
- Change host to `0.0.0.0` to allow network access
- **Warning**: Only use on trusted networks
- Consider adding authentication for production use

---

## 🚀 Performance Optimization

### For Low-End Systems
```bash
INFERENCE_SIZE=320
PROCESS_EVERY_N_FRAMES=2
DETECTION_CONFIDENCE=0.4
```

### For High-End Systems
```bash
INFERENCE_SIZE=640
PROCESS_EVERY_N_FRAMES=1
DETECTION_CONFIDENCE=0.6
DEVICE=cuda  # If GPU available
```

---

## 🐛 Troubleshooting

### Issue: Cannot connect to web interface
**Solution:**
- Ensure web server is running
- Check firewall settings
- Verify port 8080 is not in use
- Try http://localhost:8080 instead

### Issue: No video feed
**Solution:**
- Click "Start" button
- Check camera connection
- Verify camera permissions in Windows
- Try different camera source (0, 1, 2)

### Issue: Slow performance
**Solution:**
- Increase `PROCESS_EVERY_N_FRAMES`
- Reduce `INFERENCE_SIZE`
- Close other applications
- Check CPU usage

### Issue: Violations not detected
**Solution:**
- Lower confidence threshold
- Ensure good lighting
- Check camera positioning
- Verify model files exist

---

## 📚 Documentation

- **[WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md)** - Comprehensive user guide
- **[FRONTEND_SUMMARY.md](FRONTEND_SUMMARY.md)** - Feature overview
- **[WINDOWS_SETUP_GUIDE.md](WINDOWS_SETUP_GUIDE.md)** - Installation instructions
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment guide

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern web framework
- **WebSocket** - Real-time communication
- **SQLite** - Database
- **OpenCV** - Video processing
- **Ultralytics YOLO** - Object detection

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling
- **JavaScript** - Interactivity
- **WebSocket API** - Real-time updates

---

## 📈 System Requirements

### Minimum
- Windows 10/11
- 4GB RAM
- Dual-core CPU
- Webcam
- Modern web browser

### Recommended
- Windows 10/11
- 8GB+ RAM
- Quad-core CPU
- HD Webcam
- Chrome/Firefox/Edge (latest)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Ultralytics YOLO for object detection
- FastAPI for the web framework
- OpenCV for video processing

---

## 📞 Support

For issues or questions:
1. Check the documentation in the `docs/` folder
2. Review system logs in `logs/edge_system.log`
3. Open an issue on GitHub

---

**Built with ❤️ for traffic safety monitoring**

🚦 **Happy Monitoring!** 🤖
