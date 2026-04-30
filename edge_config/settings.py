#!/usr/bin/env python3
"""
Edge Deployment Settings
Loads environment variables for Raspberry Pi 5 edge deployment.
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass


class EdgeSettings:
    """Edge deployment settings loaded from environment"""
    
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "Embedded Traffic Violation Detection")
        self.app_version = os.getenv("APP_VERSION", "1.0.0-edge")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Device
        self.device = os.getenv("DEVICE", "cpu")
        self.inference_size = int(os.getenv("INFERENCE_SIZE", "320"))
        self.num_threads = int(os.getenv("NUM_THREADS", "4"))
        self.target_fps = int(os.getenv("TARGET_FPS", "15"))
        
        # Camera
        self.camera_source = self._parse_camera_source(os.getenv("CAMERA_SOURCE", "0"))
        self.camera_width = int(os.getenv("CAMERA_WIDTH", "1280"))
        self.camera_height = int(os.getenv("CAMERA_HEIGHT", "720"))
        self.camera_fps = int(os.getenv("CAMERA_FPS", "30"))
        self.camera_backend = os.getenv("CAMERA_BACKEND", "v4l2")
        
        # Models
        project_root = Path(__file__).parent.parent
        self.yolo_model_path = str(project_root / os.getenv("YOLO_MODEL_PATH", "models/best.pt"))
        self.onnx_model_path = str(project_root / os.getenv("ONNX_MODEL_PATH", "models/best.onnx"))
        self.helmet_model_path = str(project_root / os.getenv("HELMET_MODEL_PATH", "models/yolo11nHelmet_Detection_using_Yolo11.pt"))
        self.plate_model_path = str(project_root / os.getenv("PLATE_MODEL_PATH", "models/yolo11n_numberplate.pt"))
        
        # Detection
        self.detection_confidence = float(os.getenv("DETECTION_CONFIDENCE", "0.50"))
        self.nms_iou_threshold = float(os.getenv("NMS_IOU_THRESHOLD", "0.45"))
        self.ocr_confidence = float(os.getenv("OCR_CONFIDENCE", "0.5"))
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{project_root / 'data' / 'violations.db'}")
        
        # API
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # GPS
        self.gps_mode = os.getenv("GPS_MODE", "real")
        self.default_latitude = float(os.getenv("DEFAULT_LATITUDE", "18.5204"))
        self.default_longitude = float(os.getenv("DEFAULT_LONGITUDE", "73.8567"))
        
        # Display
        self.show_display = os.getenv("SHOW_DISPLAY", "False").lower() == "true"
        
        # LLM
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.always_verify_with_llm = os.getenv("ALWAYS_VERIFY_WITH_LLM", "False").lower() == "true"
        
        # Performance
        self.process_every_n_frames = int(os.getenv("PROCESS_EVERY_N_FRAMES", "1"))
        self.max_evidence_images = int(os.getenv("MAX_EVIDENCE_IMAGES", "5000"))
        self.auto_cleanup_days = int(os.getenv("AUTO_CLEANUP_DAYS", "90"))
        
        # Speed Detection
        self.pixels_per_meter = float(os.getenv("PIXELS_PER_METER", "8.0"))
        self.speed_limit_kmh = float(os.getenv("SPEED_LIMIT_KMH", "60.0"))
        self.speed_violation_threshold = float(os.getenv("SPEED_VIOLATION_THRESHOLD", "60.0"))
        self.min_track_length_speed = int(os.getenv("MIN_TRACK_LENGTH_SPEED", "5"))
        
        # Paths
        self.evidence_dir = str(project_root / "data" / "evidence")
        self.reports_dir = str(project_root / "data" / "reports")
        self.logs_dir = str(project_root / "logs")
    
    @staticmethod
    def _parse_camera_source(source: str):
        """Parse camera source - int for device index, str for file path"""
        try:
            return int(source)
        except ValueError:
            return source
    
    def print_summary(self):
        """Print settings summary"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║          EDGE SETTINGS SUMMARY                              ║
╠══════════════════════════════════════════════════════════════╣
║  App:         {self.app_name:<44} ║
║  Version:     {self.app_version:<44} ║
║  Debug:       {str(self.debug):<44} ║
╠──────────────────────────────────────────────────────────────╣
║  Device:      {self.device:<44} ║
║  Inference:   {f'{self.inference_size}×{self.inference_size}':<44} ║
║  Threads:     {str(self.num_threads):<44} ║
║  Target FPS:  {str(self.target_fps):<44} ║
╠──────────────────────────────────────────────────────────────╣
║  Camera:      {f'Source {self.camera_source} @ {self.camera_width}×{self.camera_height}':<44} ║
║  Display:     {str(self.show_display):<44} ║
║  GPS Mode:    {self.gps_mode:<44} ║
╠──────────────────────────────────────────────────────────────╣
║  Speed Limit: {f'{self.speed_limit_kmh} km/h':<44} ║
║  PPM:         {f'{self.pixels_per_meter} pixels/meter':<44} ║
╠──────────────────────────────────────────────────────────────╣
║  API:         {f'http://{self.api_host}:{self.api_port}':<44} ║
║  Database:    {self.database_url[:44]:<44} ║
║  LLM:         {'Enabled' if self.gemini_api_key else 'Disabled':<44} ║
╚══════════════════════════════════════════════════════════════╝
""")


@lru_cache()
def get_settings() -> EdgeSettings:
    """Get singleton settings instance"""
    return EdgeSettings()


if __name__ == "__main__":
    settings = get_settings()
    settings.print_summary()
