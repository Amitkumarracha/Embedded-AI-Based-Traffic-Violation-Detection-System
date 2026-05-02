#!/usr/bin/env python3
"""
Web Server for Traffic Violation Detection System
Provides real-time web interface with WebSocket support
"""

import asyncio
import base64
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Set
import cv2
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi import Request
import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from edge_config.settings import get_settings
from edge_database.connection import get_session
from edge_database.crud import get_violations, get_violation_count

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Traffic Violation Detection System")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web_frontend/static"), name="static")
templates = Jinja2Templates(directory="web_frontend/templates")

# Global state
class SystemState:
    def __init__(self):
        self.is_running = False
        self.current_frame = None
        self.fps = 0
        self.active_connections: Set[WebSocket] = set()
        self.stats = {
            'total_violations': 0,
            'today_violations': 0,
            'active_detections': 0,
            'system_uptime': 0
        }
        self.settings = get_settings()
        
state = SystemState()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()


# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Send initial stats
        await websocket.send_json({
            'type': 'stats',
            'data': state.stats
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(websocket, data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, data: dict):
    """Handle incoming WebSocket messages"""
    msg_type = data.get('type')
    
    if msg_type == 'command':
        command = data.get('command')
        
        if command == 'start':
            await start_detection()
            await manager.broadcast({
                'type': 'log',
                'level': 'info',
                'message': 'Detection system started'
            })
            
        elif command == 'stop':
            await stop_detection()
            await manager.broadcast({
                'type': 'log',
                'level': 'info',
                'message': 'Detection system stopped'
            })
            
        elif command == 'get_stats':
            await update_stats()
            await websocket.send_json({
                'type': 'stats',
                'data': state.stats
            })
            
        elif command == 'update_settings':
            settings_data = data.get('data', {})
            await update_settings(settings_data)
            await manager.broadcast({
                'type': 'log',
                'level': 'info',
                'message': 'Settings updated successfully'
            })


async def start_detection():
    """Start the detection system"""
    if not state.is_running:
        state.is_running = True
        asyncio.create_task(detection_loop())
        logger.info("Detection system started")


async def stop_detection():
    """Stop the detection system"""
    state.is_running = False
    logger.info("Detection system stopped")


async def detection_loop():
    """Main detection loop"""
    import cv2
    from edge_core.detector import Detector
    
    # Initialize detector
    try:
        detector = Detector(
            model_path=state.settings.yolo_model_path,
            inference_size=state.settings.inference_size,
            device=state.settings.device
        )
        logger.info("Detector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        await manager.broadcast({
            'type': 'log',
            'level': 'error',
            'message': f'Failed to initialize detector: {str(e)}'
        })
        state.is_running = False
        return
    
    # Open camera
    camera_source = state.settings.camera_source
    if isinstance(camera_source, str) and camera_source.isdigit():
        camera_source = int(camera_source)
    
    cap = cv2.VideoCapture(camera_source)
    
    if not cap.isOpened():
        logger.error(f"Failed to open camera: {camera_source}")
        await manager.broadcast({
            'type': 'log',
            'level': 'error',
            'message': f'Failed to open camera: {camera_source}'
        })
        state.is_running = False
        return
    
    logger.info(f"Camera opened: {camera_source}")
    frame_count = 0
    
    try:
        while state.is_running:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning("Failed to read frame from camera")
                await asyncio.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Process frame
            if frame_count % state.settings.process_every_n_frames == 0:
                try:
                    # Run detection
                    results = detector.detect(frame)
                    
                    # Draw detections on frame
                    annotated_frame = frame.copy()
                    for detection in results:
                        x1, y1, x2, y2 = map(int, detection['bbox'])
                        label = f"{detection['class_name']} {detection['confidence']:.2f}"
                        
                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(annotated_frame, label, (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Encode frame to JPEG
                    _, buffer = cv2.imencode('.jpg', annotated_frame)
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Broadcast frame to all clients
                    await manager.broadcast({
                        'type': 'frame',
                        'data': frame_base64
                    })
                    
                    # Check for violations
                    if len(results) > 0:
                        state.stats['active_detections'] = len(results)
                        
                        # Simulate violation detection (you can add your logic here)
                        for detection in results:
                            if detection['class_name'] in ['person', 'motorcycle']:
                                violation = {
                                    'type': 'No Helmet Detected',
                                    'timestamp': datetime.now().isoformat(),
                                    'details': f"Detected {detection['class_name']} without helmet",
                                    'confidence': detection['confidence'],
                                    'plate': None
                                }
                                
                                await manager.broadcast({
                                    'type': 'violation',
                                    'data': violation
                                })
                    
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.03)  # ~30 FPS
            
    except Exception as e:
        logger.error(f"Detection loop error: {e}")
    finally:
        cap.release()
        state.is_running = False
        logger.info("Detection loop stopped")


async def update_stats():
    """Update system statistics"""
    try:
        state.stats['total_violations'] = get_violation_count()
        # For today's violations, we'll use the same count for now
        state.stats['today_violations'] = get_violation_count()
    except Exception as e:
        logger.error(f"Error updating stats: {e}")


async def update_settings(settings_data: dict):
    """Update system settings"""
    try:
        if 'confidence' in settings_data:
            state.settings.detection_confidence = float(settings_data['confidence'])
        if 'speedLimit' in settings_data:
            state.settings.speed_limit_kmh = float(settings_data['speedLimit'])
        if 'processFrames' in settings_data:
            state.settings.process_every_n_frames = int(settings_data['processFrames'])
        
        logger.info(f"Settings updated: {settings_data}")
    except Exception as e:
        logger.error(f"Error updating settings: {e}")


@app.get("/api/violations/recent")
async def get_recent_violations_api():
    """Get recent violations"""
    try:
        violations = get_violations(limit=20)
        
        return [
            {
                'id': v.id,
                'type': v.violation_type,
                'timestamp': v.timestamp.isoformat(),
                'details': f"Confidence: {v.confidence:.2f}",
                'plate': v.plate_number
            }
            for v in violations
        ]
    except Exception as e:
        logger.error(f"Error fetching violations: {e}")
        return []


@app.get("/api/violations/export")
async def export_violations():
    """Export violations to CSV"""
    try:
        violations = get_violations(limit=1000)
        
        # Create CSV content
        csv_content = "ID,Type,Timestamp,Confidence,License Plate\n"
        for v in violations:
            csv_content += f"{v.id},{v.violation_type},{v.timestamp},{v.confidence},{v.plate_number or 'N/A'}\n"
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=violations.csv"}
        )
    except Exception as e:
        logger.error(f"Error exporting violations: {e}")
        return {"error": str(e)}


@app.get("/api/stats")
async def get_stats_api():
    """Get current system statistics"""
    await update_stats()
    return state.stats


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Traffic Violation Detection Web Server")
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("evidence").mkdir(exist_ok=True)
    
    # Update initial stats
    await update_stats()
    
    logger.info("Web server initialized successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down web server")
    state.is_running = False


def main():
    """Run the web server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Traffic Violation Detection Web Server")
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on http://{args.host}:{args.port}")
    
    uvicorn.run(
        "web_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
