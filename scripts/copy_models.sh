#!/bin/bash
# Script to copy model weights from main backend to edge deployment folder
# Run this on your development machine before transferring to Raspberry Pi

set -e

echo "=" * 70
echo "Copy Models to Edge Deployment Folder"
echo "=" * 70

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
EDGE_DIR="$PROJECT_ROOT/Embedded AI-Based Traffic Violation Detection System"
MODELS_DIR="$EDGE_DIR/models"

echo "Project Root: $PROJECT_ROOT"
echo "Edge Directory: $EDGE_DIR"
echo "Models Directory: $MODELS_DIR"
echo ""

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

# Copy main YOLO model
if [ -f "$PROJECT_ROOT/backend/yolov8n.pt" ]; then
    echo "✓ Copying yolov8n.pt → best.pt"
    cp "$PROJECT_ROOT/backend/yolov8n.pt" "$MODELS_DIR/best.pt"
else
    echo "⚠ yolov8n.pt not found in backend/"
fi

# Copy ONNX model if available
if [ -f "$PROJECT_ROOT/backend/best.onnx" ]; then
    echo "✓ Copying best.onnx"
    cp "$PROJECT_ROOT/backend/best.onnx" "$MODELS_DIR/best.onnx"
else
    echo "⚠ best.onnx not found (optional)"
fi

# Copy helmet detection model
if [ -f "$PROJECT_ROOT/backend/yolov8n-pose.pt" ]; then
    echo "✓ Copying yolov8n-pose.pt → yolo11nHelmet_Detection_using_Yolo11.pt"
    cp "$PROJECT_ROOT/backend/yolov8n-pose.pt" "$MODELS_DIR/yolo11nHelmet_Detection_using_Yolo11.pt"
else
    echo "⚠ yolov8n-pose.pt not found (optional)"
fi

# Copy number plate model if available
if [ -f "$PROJECT_ROOT/model/checkpoints/yolo11n_numberplate.pt" ]; then
    echo "✓ Copying yolo11n_numberplate.pt"
    cp "$PROJECT_ROOT/model/checkpoints/yolo11n_numberplate.pt" "$MODELS_DIR/yolo11n_numberplate.pt"
else
    echo "⚠ yolo11n_numberplate.pt not found (optional)"
fi

echo ""
echo "=" * 70
echo "Models copied successfully!"
echo "=" * 70
echo ""
echo "Next steps:"
echo "1. Transfer entire 'Embedded AI-Based Traffic Violation Detection System' folder to Raspberry Pi"
echo "2. Run setup script on Raspberry Pi: ./setup_rpi5.sh"
echo "3. Start system: python run_edge.py --mode full"
echo ""
echo "Transfer command (from Windows/Linux):"
echo "  scp -r \"$EDGE_DIR\" pi@raspberrypi.local:~/"
