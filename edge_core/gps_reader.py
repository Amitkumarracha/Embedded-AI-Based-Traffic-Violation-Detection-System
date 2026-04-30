#!/usr/bin/env python3
"""
Edge GPS Reader
Supports real GPS (gpsd) and mock GPS for development
"""

import threading
import time
import random
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import gpsd
    GPSD_AVAILABLE = True
except ImportError:
    GPSD_AVAILABLE = False
    logger.info("gpsd not available - using mock GPS")


@dataclass
class GPSLocation:
    """GPS location data"""
    latitude: float
    longitude: float
    accuracy_meters: float
    timestamp: datetime
    is_mock: bool
    
    def __str__(self):
        mock_str = " (MOCK)" if self.is_mock else ""
        return f"GPS{mock_str}: {self.latitude:.6f}°N, {self.longitude:.6f}°E"


class EdgeGPSReader:
    """GPS reader for edge deployment"""
    
    def __init__(self, mock_center: Tuple[float, float] = (18.5204, 73.8567)):
        self.mock_center = mock_center
        self.use_real_gps = self._should_use_real_gps()
        
        self._location: Optional[GPSLocation] = None
        self._location_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        
        # Mock GPS state
        self._mock_lat = mock_center[0]
        self._mock_lon = mock_center[1]
        
        logger.info(f"GPS Reader initialized | Mode: {'REAL' if self.use_real_gps else 'MOCK'}")
    
    def _should_use_real_gps(self) -> bool:
        """Detect if real GPS should be used"""
        if not GPSD_AVAILABLE:
            return False
        
        try:
            device_tree = Path("/proc/device-tree/model")
            if device_tree.exists():
                with open(device_tree, "rb") as f:
                    if "Raspberry Pi" in f.read().decode("utf-8", errors="ignore"):
                        return True
        except Exception:
            pass
        
        return False
    
    def start(self):
        """Start GPS reading thread"""
        if self._thread and self._thread.is_alive():
            return
        
        self._stop_event.clear()
        
        if self.use_real_gps:
            self._thread = threading.Thread(target=self._real_gps_loop, daemon=True)
        else:
            self._thread = threading.Thread(target=self._mock_gps_loop, daemon=True)
        
        self._thread.start()
        logger.info(f"GPS thread started ({'REAL' if self.use_real_gps else 'MOCK'} mode)")
    
    def stop(self):
        """Stop GPS thread"""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=2.0)
    
    def get_location(self) -> Optional[GPSLocation]:
        """Get current GPS location"""
        with self._location_lock:
            return self._location
    
    def _real_gps_loop(self):
        """Real GPS reading loop"""
        try:
            gpsd.connect()
            logger.info("✓ Connected to gpsd")
            
            while not self._stop_event.is_set():
                try:
                    packet = gpsd.get_current()
                    
                    if packet.mode >= 2:
                        location = GPSLocation(
                            latitude=packet.lat,
                            longitude=packet.lon,
                            accuracy_meters=packet.error.get('epx', 2.5),
                            timestamp=datetime.now(),
                            is_mock=False
                        )
                        
                        with self._location_lock:
                            self._location = location
                    
                    time.sleep(1.0)
                
                except Exception as e:
                    logger.error(f"GPS read error: {e}")
                    time.sleep(1.0)
        
        except Exception as e:
            logger.error(f"Failed to connect to gpsd: {e}")
            self._mock_gps_loop()
    
    def _mock_gps_loop(self):
        """Mock GPS loop"""
        logger.warning("⚠️ MOCK GPS MODE - For development only!")
        
        while not self._stop_event.is_set():
            # Simulate small random movement
            self._mock_lat += random.uniform(-0.0001, 0.0001)
            self._mock_lon += random.uniform(-0.0001, 0.0001)
            
            location = GPSLocation(
                latitude=self._mock_lat,
                longitude=self._mock_lon,
                accuracy_meters=0.0,
                timestamp=datetime.now(),
                is_mock=True
            )
            
            with self._location_lock:
                self._location = location
            
            time.sleep(1.0)
