#!/bin/bash
# Install systemd service for auto-start on boot

set -e

echo "Installing Traffic Violation Detection System service..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Update service file with correct paths
SERVICE_FILE="$SCRIPT_DIR/traffic-detector.service"
TEMP_SERVICE="/tmp/traffic-detector.service"

# Replace placeholder paths with actual paths
sed "s|/home/pi/Embedded AI-Based Traffic Violation Detection System|$PROJECT_DIR|g" "$SERVICE_FILE" > "$TEMP_SERVICE"

# Copy service file to systemd
sudo cp "$TEMP_SERVICE" /etc/systemd/system/traffic-detector.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable traffic-detector.service

echo "✅ Service installed successfully!"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start traffic-detector"
echo "  Stop:    sudo systemctl stop traffic-detector"
echo "  Status:  sudo systemctl status traffic-detector"
echo "  Logs:    sudo journalctl -u traffic-detector -f"
echo "  Disable: sudo systemctl disable traffic-detector"
echo ""
echo "The system will now start automatically on boot."
