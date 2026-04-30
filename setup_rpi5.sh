#!/bin/bash
# ============================================================================
# Raspberry Pi 5 - Embedded Traffic Violation Detection System Setup
# One-click setup script for edge deployment
# ============================================================================

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Embedded AI-Based Traffic Violation Detection System       ║"
echo "║  Raspberry Pi 5 Setup Script                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================================
# Step 1: System Update
# ============================================================================
echo -e "${CYAN}[1/8] Updating system packages...${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
echo -e "${GREEN}✓ System updated${NC}"

# ============================================================================
# Step 2: Install System Dependencies
# ============================================================================
echo -e "${CYAN}[2/8] Installing system dependencies...${NC}"
sudo apt-get install -y -qq \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    v4l-utils \
    libv4l-dev \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbbmalloc2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gpsd \
    gpsd-clients \
    libgps-dev \
    sqlite3 \
    git \
    wget \
    curl \
    htop \
    2>/dev/null || true

echo -e "${GREEN}✓ System dependencies installed${NC}"

# ============================================================================
# Step 3: Create Python Virtual Environment
# ============================================================================
echo -e "${CYAN}[3/8] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}  Virtual environment already exists${NC}"
fi

source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel -q

echo -e "${GREEN}✓ Virtual environment ready${NC}"

# ============================================================================
# Step 4: Install Python Dependencies
# ============================================================================
echo -e "${CYAN}[4/8] Installing Python dependencies (this takes ~15-20 minutes)...${NC}"

# Install PyTorch for ARM64 (CPU only)
echo "  Installing PyTorch (ARM64 CPU)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu -q 2>/dev/null || \
pip install torch torchvision -q

# Install main requirements
echo "  Installing project dependencies..."
pip install -r requirements_rpi5.txt -q

echo -e "${GREEN}✓ Python dependencies installed${NC}"

# ============================================================================
# Step 5: Create Data Directories
# ============================================================================
echo -e "${CYAN}[5/8] Creating data directories...${NC}"
mkdir -p data/evidence
mkdir -p data/reports
mkdir -p logs
mkdir -p models

echo -e "${GREEN}✓ Data directories created${NC}"

# ============================================================================
# Step 6: Setup Environment Configuration
# ============================================================================
echo -e "${CYAN}[6/8] Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.rpi .env
    echo -e "${GREEN}✓ Environment file created from template${NC}"
else
    echo -e "${YELLOW}  .env already exists, skipping${NC}"
fi

# ============================================================================
# Step 7: Configure Camera & GPU Memory
# ============================================================================
echo -e "${CYAN}[7/8] Configuring camera and system settings...${NC}"

# Enable camera in config.txt if not already
CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

if [ -f "$CONFIG_FILE" ]; then
    # Increase GPU memory for video processing
    if ! grep -q "gpu_mem=256" "$CONFIG_FILE" 2>/dev/null; then
        echo "" | sudo tee -a "$CONFIG_FILE" > /dev/null
        echo "# Traffic Violation Detection System" | sudo tee -a "$CONFIG_FILE" > /dev/null
        echo "gpu_mem=256" | sudo tee -a "$CONFIG_FILE" > /dev/null
        echo -e "${YELLOW}  ⚠ GPU memory set to 256MB (reboot required)${NC}"
    fi
fi

# Test camera availability
echo "  Testing camera..."
if v4l2-ctl --list-devices 2>/dev/null | grep -q "video"; then
    echo -e "${GREEN}  ✓ USB camera detected${NC}"
    v4l2-ctl --list-devices 2>/dev/null || true
else
    echo -e "${YELLOW}  ⚠ No USB camera detected. Connect webcam and re-run test.${NC}"
fi

echo -e "${GREEN}✓ System configured${NC}"

# ============================================================================
# Step 8: Verify Installation
# ============================================================================
echo -e "${CYAN}[8/8] Verifying installation...${NC}"

python3 -c "
import sys
print(f'  Python: {sys.version}')

# Check critical packages
checks = []

try:
    import cv2
    checks.append(('OpenCV', cv2.__version__, True))
except ImportError:
    checks.append(('OpenCV', 'NOT FOUND', False))

try:
    import torch
    checks.append(('PyTorch', torch.__version__, True))
except ImportError:
    checks.append(('PyTorch', 'NOT FOUND', False))

try:
    import onnxruntime as ort
    checks.append(('ONNXRuntime', ort.__version__, True))
except ImportError:
    checks.append(('ONNXRuntime', 'NOT FOUND', False))

try:
    import numpy as np
    checks.append(('NumPy', np.__version__, True))
except ImportError:
    checks.append(('NumPy', 'NOT FOUND', False))

try:
    import fastapi
    checks.append(('FastAPI', fastapi.__version__, True))
except ImportError:
    checks.append(('FastAPI', 'NOT FOUND', False))

try:
    import sqlalchemy
    checks.append(('SQLAlchemy', sqlalchemy.__version__, True))
except ImportError:
    checks.append(('SQLAlchemy', 'NOT FOUND', False))

try:
    import ultralytics
    checks.append(('Ultralytics', ultralytics.__version__, True))
except ImportError:
    checks.append(('Ultralytics', 'NOT FOUND', False))

all_ok = True
for name, version, ok in checks:
    status = '✓' if ok else '✗'
    print(f'  {status} {name}: {version}')
    if not ok:
        all_ok = False

if all_ok:
    print()
    print('  ✅ All dependencies verified!')
else:
    print()
    print('  ⚠️  Some dependencies are missing. Check output above.')
"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                         ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Next Steps:                                               ║"
echo "║  1. Copy model weights to models/ directory                ║"
echo "║  2. Connect USB webcam                                     ║"
echo "║  3. Activate venv:  source venv/bin/activate               ║"
echo "║  4. Run system:     python run_edge.py --mode full         ║"
echo "║  5. Dashboard:      http://$(hostname -I | awk '{print $1}'):8000     ║"
echo "║                                                            ║"
echo "║  Optional:                                                 ║"
echo "║  • Install as service: sudo bash services/install_service.sh║"
echo "║  • Benchmark:    python scripts/benchmark.py               ║"
echo "║  • Test camera:  python scripts/test_camera.py             ║"
echo "║                                                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
