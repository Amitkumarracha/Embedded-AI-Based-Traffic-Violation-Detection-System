# 🚦 Embedded AI-Based Traffic Violation Detection System
## Raspberry Pi 5 Edge Deployment Package

> **Complete self-contained edge AI system** for real-time traffic violation detection 
> using USB webcam on Raspberry Pi 5. Detects helmet violations, triple riding, 
> number plate recognition with SRGAN enhancement, OCR, GPS logging, and automated reporting.

---

## 📋 System Architecture

```
USB Webcam (1280×720 @ 30fps)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Raspberry Pi 5  (8GB RAM, ARM Cortex-A76)          │
│                                                     │
│  Thread 1: Camera Capture (USB Webcam via V4L2)     │
│      │                                              │
│      ▼                                              │
│  Thread 2: Preprocessing (CLAHE, Letterbox)         │
│      │                                              │
│      ▼                                              │
│  Thread 3: YOLO Inference (INT8 ONNX, 320×320)     │
│      │        + DeepSort Tracking                   │
│      │        + Violation Gate (4-stage filter)      │
│      ▼                                              │
│  Thread 4: Logging & Reporting                      │
│      │   • SRGAN plate enhancement                  │
│      │   • PaddleOCR plate reading                  │
│      │   • GPS coordinate logging                   │
│      │   • SQLite database storage                  │
│      │   • PDF report generation                    │
│      ▼                                              │
│  FastAPI Dashboard (Port 8000)                      │
│      • Real-time WebSocket feed                     │
│      • Violation history & analytics                │
│      • Evidence image viewer                        │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Hardware Requirements

| Component | Specification | Notes |
|-----------|--------------|-------|
| **Board** | Raspberry Pi 5 (8GB) | 4GB works but 8GB recommended |
| **Storage** | 64GB+ microSD (Class 10/U3) | Or NVMe SSD via HAT |
| **Camera** | USB Webcam (UVC compatible) | Logitech C920/C270 tested |
| **GPS** | USB GPS Module (optional) | VK-162 G-Mouse recommended |
| **Power** | 27W USB-C PD (5V/5A) | Official Pi 5 PSU recommended |
| **Cooling** | Active cooler / heatsink | Required for sustained AI inference |
| **Network** | Wi-Fi / Ethernet | For dashboard access |

---

## 🚀 Quick Start

### 1. Flash Raspberry Pi OS
```bash
# Use Raspberry Pi Imager to flash:
# Raspberry Pi OS (64-bit) Bookworm - Desktop or Lite
```

### 2. Transfer This Folder
```bash
# From your Windows PC:
scp -r "Embedded AI-Based Traffic Violation Detection System" pi@raspberrypi.local:~/

# Or use USB drive / network share
```

### 3. Run Setup
```bash
cd ~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/
chmod +x setup_rpi5.sh
./setup_rpi5.sh
```

### 4. Copy Your Model Weights
```bash
# Copy from your trained models (on Windows PC):
scp "model/checkpoints/best.pt" pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/
scp "model/checkpoints/best.onnx" pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/
scp "model/checkpoints/yolo11nHelmet_Detection_using_Yolo11.pt" pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/
scp "model/checkpoints/yolo11n_numberplate.pt" pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/
```

### 5. Start the System
```bash
# Activate environment
source venv/bin/activate

# Start full system (headless mode - recommended for RPi)
python run_edge.py --mode full --no-display

# Or with display (if HDMI monitor connected)
python run_edge.py --mode full

# API dashboard accessible at:
# http://raspberrypi.local:8000
```

---

## 📂 Folder Structure

```
Embedded AI-Based Traffic Violation Detection System/
├── README.md                    # This file
├── setup_rpi5.sh               # One-click setup script
├── requirements_rpi5.txt       # RPi-optimized dependencies
├── run_edge.py                 # Main entry point for edge deployment
├── .env.rpi                    # Environment config for RPi
│
├── edge_config/                # RPi-specific configuration
│   ├── __init__.py
│   ├── platform_config.py      # RPi 5 hardware detection & tuning
│   └── settings.py             # Edge deployment settings
│
├── edge_core/                  # Core detection modules (RPi-optimized)
│   ├── __init__.py
│   ├── detector.py             # ONNX-based YOLO detector
│   ├── tracker.py              # DeepSort vehicle tracker
│   ├── violation_gate.py       # 4-stage violation filter
│   ├── ocr.py                  # License plate OCR
│   ├── gps_reader.py           # GPS module interface
│   └── plate_enhancer.py       # SRGAN/Real-ESRGAN enhancer
│
├── edge_pipeline/              # Multi-threaded processing pipeline
│   ├── __init__.py
│   ├── camera_stream.py        # USB webcam capture (V4L2)
│   ├── main_pipeline.py        # 4-thread orchestrator
│   └── video_processor.py      # Video file processing
│
├── edge_api/                   # Lightweight REST API + dashboard
│   ├── __init__.py
│   ├── app.py                  # FastAPI application
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── violations.py       # Violation CRUD
│   │   ├── health.py           # System health monitoring
│   │   ├── camera.py           # Camera control
│   │   └── analytics.py        # Statistics & analytics
│   └── templates/              # Lightweight HTML dashboard
│       └── dashboard.html      # Single-page dashboard
│
├── edge_database/              # SQLite database layer
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy models
│   ├── connection.py           # DB connection management
│   └── crud.py                 # CRUD operations
│
├── edge_reporting/             # Violation reporting
│   ├── __init__.py
│   ├── pdf_generator.py        # PDF report generation
│   └── alert_sender.py         # Email/SMS alerts
│
├── models/                     # AI model weights (copy here)
│   ├── .gitkeep
│   └── README.md               # Model placement instructions
│
├── data/                       # Runtime data
│   ├── violations.db           # SQLite database (auto-created)
│   ├── evidence/               # Violation evidence images
│   └── reports/                # Generated PDF reports
│
├── scripts/                    # Utility scripts
│   ├── quantize_int8.py        # INT8 quantization for ARM
│   ├── benchmark.py            # Performance benchmarking
│   ├── test_camera.py          # USB webcam test
│   ├── test_gps.py             # GPS module test
│   └── export_onnx.py         # PyTorch to ONNX export
│
├── services/                   # Systemd service files
│   ├── traffic-detector.service # Auto-start on boot
│   └── install_service.sh      # Service installer
│
└── logs/                       # Application logs
    └── .gitkeep
```

---

## 📊 Performance Targets (Raspberry Pi 5)

| Metric | FP32 (640px) | FP32 (320px) | INT8 (320px) |
|--------|-------------|-------------|-------------|
| Inference | 3-5 FPS | 8-12 FPS | 15-25 FPS |
| Latency | ~300ms | ~120ms | ~60ms |
| RAM | ~2.5 GB | ~1.8 GB | ~1.2 GB |
| Model Size | 9.3 MB | 9.3 MB | ~2.5 MB |

**Recommended:** INT8 @ 320×320 for real-time operation.

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard (HTML) |
| `/api/health` | GET | System health status |
| `/api/violations` | GET | List violations |
| `/api/violations/{id}` | GET | Get specific violation |
| `/api/violations/{id}/image` | GET | Evidence image |
| `/api/violations/stats` | GET | Violation statistics |
| `/api/camera/status` | GET | Camera status |
| `/api/camera/snapshot` | GET | Live snapshot |
| `/ws/live` | WS | Real-time violation feed |

---

## 🔌 USB Webcam Setup

The system auto-detects USB webcams connected to any USB port on the Raspberry Pi 5.

```bash
# Check connected cameras
v4l2-ctl --list-devices

# Test camera
python scripts/test_camera.py

# Specify camera source (default: /dev/video0 = source 0)
python run_edge.py --source 0         # First USB camera
python run_edge.py --source 1         # Second USB camera  
python run_edge.py --source video.mp4 # Test with video file
```

---

## 📄 License

MIT License - See main project for full details.
