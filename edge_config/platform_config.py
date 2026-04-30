#!/usr/bin/env python3
"""
Raspberry Pi 5 Platform Configuration
Auto-detects hardware capabilities and provides optimized inference settings.
Includes thermal monitoring for sustained operation.
"""

import os
import platform
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


# ============================================================================
# PLATFORM CONFIG
# ============================================================================

@dataclass
class PlatformConfig:
    """Hardware-specific configuration for edge inference"""
    platform: str              # 'raspberry_pi_5', 'raspberry_pi_4', 'generic_arm', 'x86_cpu'
    device_name: str           # Human-readable device name
    inference_size: int        # YOLO input size (320 for RPi5, 416 for x86)
    num_threads: int           # CPU threads for ONNX inference
    max_fps_target: int        # Target FPS for real-time
    confidence_threshold: float
    model_path: str            # Path to model weights
    use_int8: bool             # Use INT8 quantized model
    camera_width: int          # Camera capture width
    camera_height: int         # Camera capture height
    camera_fps: int            # Camera target FPS
    gpu_memory_mb: int         # Allocated GPU memory
    cpu_cores: int             # Available CPU cores
    ram_mb: int                # Available RAM in MB

    def __str__(self):
        return f"""
╔══════════════════════════════════════════════════════════════╗
║          EDGE PLATFORM CONFIGURATION                        ║
╠══════════════════════════════════════════════════════════════╣
║  Platform:        {self.platform:<40} ║
║  Device:          {self.device_name:<40} ║
║  CPU Cores:       {str(self.cpu_cores):<40} ║
║  RAM:             {f'{self.ram_mb} MB':<40} ║
║  GPU Memory:      {f'{self.gpu_memory_mb} MB':<40} ║
╠══════════════════════════════════════════════════════════════╣
║  Inference Size:  {f'{self.inference_size}×{self.inference_size}':<40} ║
║  Target FPS:      {str(self.max_fps_target):<40} ║
║  Confidence:      {str(self.confidence_threshold):<40} ║
║  Threads:         {str(self.num_threads):<40} ║
║  INT8 Quantized:  {('✅ YES' if self.use_int8 else '❌ NO'):<40} ║
╠══════════════════════════════════════════════════════════════╣
║  Camera:          {f'{self.camera_width}×{self.camera_height} @ {self.camera_fps}fps':<40} ║
║  Model:           {Path(self.model_path).name:<40} ║
╚══════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# HARDWARE DETECTION
# ============================================================================

def is_raspberry_pi() -> bool:
    """Check if running on any Raspberry Pi"""
    try:
        device_tree = Path("/proc/device-tree/model")
        if device_tree.exists():
            with open(device_tree, "rb") as f:
                content = f.read().decode("utf-8", errors="ignore")
                return "Raspberry Pi" in content
    except Exception:
        pass
    
    # Fallback: check architecture
    return platform.machine() in ['aarch64', 'armv7l', 'armv6l']


def is_raspberry_pi_5() -> bool:
    """Check if running on Raspberry Pi 5 specifically"""
    try:
        device_tree = Path("/proc/device-tree/model")
        if device_tree.exists():
            with open(device_tree, "rb") as f:
                content = f.read().decode("utf-8", errors="ignore")
                return "Raspberry Pi 5" in content
    except Exception:
        pass
    return False


def get_cpu_count() -> int:
    """Get number of CPU cores"""
    try:
        return os.cpu_count() or 4
    except Exception:
        return 4


def get_ram_mb() -> int:
    """Get total RAM in MB"""
    try:
        import psutil
        return int(psutil.virtual_memory().total / (1024 * 1024))
    except ImportError:
        # Fallback: read from /proc/meminfo
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        return int(line.split()[1]) // 1024
        except Exception:
            pass
    return 4096  # Default 4GB


def get_cpu_temperature() -> Optional[float]:
    """Get CPU temperature in Celsius (RPi specific)"""
    try:
        # RPi thermal zone
        temp_file = Path("/sys/class/thermal/thermal_zone0/temp")
        if temp_file.exists():
            with open(temp_file, "r") as f:
                temp = int(f.read().strip()) / 1000.0
                return round(temp, 1)
    except Exception:
        pass
    
    try:
        import psutil
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    return round(entry.current, 1)
    except Exception:
        pass
    
    return None


def get_system_stats() -> Dict:
    """Get current system statistics"""
    stats = {
        "cpu_temp_c": get_cpu_temperature(),
        "cpu_count": get_cpu_count(),
        "ram_total_mb": get_ram_mb(),
        "platform": platform.machine(),
        "system": platform.system(),
        "is_rpi": is_raspberry_pi(),
        "is_rpi5": is_raspberry_pi_5(),
    }
    
    try:
        import psutil
        stats["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        stats["ram_used_percent"] = psutil.virtual_memory().percent
        stats["disk_used_percent"] = psutil.disk_usage("/").percent
    except ImportError:
        pass
    
    return stats


def detect_usb_cameras() -> list:
    """Detect available USB cameras"""
    cameras = []
    
    # Check /dev/video* devices
    for i in range(10):
        dev_path = Path(f"/dev/video{i}")
        if dev_path.exists():
            cameras.append({
                "index": i,
                "device": str(dev_path),
            })
    
    # Windows fallback
    if not cameras and platform.system() == "Windows":
        import cv2
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                cameras.append({"index": i, "device": f"Camera {i}"})
                cap.release()
    
    return cameras


# ============================================================================
# CONFIGURATION FACTORY
# ============================================================================

def get_platform_config(model_path: str = None) -> PlatformConfig:
    """
    Auto-detect platform and return optimized configuration.
    
    Args:
        model_path: Override model path (auto-detected if None)
    
    Returns:
        PlatformConfig with hardware-optimized settings
    """
    # Determine project root
    project_root = Path(__file__).parent.parent
    
    # Detect model path
    if model_path is None:
        # Priority: INT8 ONNX > FP32 ONNX > PyTorch
        model_candidates = [
            project_root / "models" / "best_int8.onnx",
            project_root / "models" / "best.onnx",
            project_root / "models" / "best.pt",
        ]
        
        model_path = None
        for candidate in model_candidates:
            if candidate.exists():
                model_path = str(candidate)
                break
        
        if model_path is None:
            model_path = str(model_candidates[-1])  # Default to .pt path
    
    # Detect INT8
    use_int8 = "int8" in str(model_path).lower()
    
    # Read environment overrides
    env_inference_size = os.environ.get("INFERENCE_SIZE")
    env_num_threads = os.environ.get("NUM_THREADS")
    env_target_fps = os.environ.get("TARGET_FPS")
    env_confidence = os.environ.get("DETECTION_CONFIDENCE")
    env_cam_w = os.environ.get("CAMERA_WIDTH")
    env_cam_h = os.environ.get("CAMERA_HEIGHT")
    env_cam_fps = os.environ.get("CAMERA_FPS")
    
    cpu_count = get_cpu_count()
    ram_mb = get_ram_mb()
    
    # Platform-specific defaults
    if is_raspberry_pi_5():
        config = PlatformConfig(
            platform="raspberry_pi_5",
            device_name="Raspberry Pi 5",
            inference_size=int(env_inference_size) if env_inference_size else 320,
            num_threads=int(env_num_threads) if env_num_threads else 4,
            max_fps_target=int(env_target_fps) if env_target_fps else 15,
            confidence_threshold=float(env_confidence) if env_confidence else 0.50,
            model_path=model_path,
            use_int8=use_int8,
            camera_width=int(env_cam_w) if env_cam_w else 1280,
            camera_height=int(env_cam_h) if env_cam_h else 720,
            camera_fps=int(env_cam_fps) if env_cam_fps else 30,
            gpu_memory_mb=256,
            cpu_cores=cpu_count,
            ram_mb=ram_mb,
        )
    elif is_raspberry_pi():
        # RPi 4 or older
        config = PlatformConfig(
            platform="raspberry_pi",
            device_name="Raspberry Pi",
            inference_size=int(env_inference_size) if env_inference_size else 320,
            num_threads=int(env_num_threads) if env_num_threads else 4,
            max_fps_target=int(env_target_fps) if env_target_fps else 10,
            confidence_threshold=float(env_confidence) if env_confidence else 0.50,
            model_path=model_path,
            use_int8=use_int8,
            camera_width=int(env_cam_w) if env_cam_w else 640,
            camera_height=int(env_cam_h) if env_cam_h else 480,
            camera_fps=int(env_cam_fps) if env_cam_fps else 15,
            gpu_memory_mb=128,
            cpu_cores=cpu_count,
            ram_mb=ram_mb,
        )
    else:
        # Generic x86 / development machine
        config = PlatformConfig(
            platform="x86_cpu",
            device_name=f"{platform.processor() or 'CPU'} ({platform.machine()})",
            inference_size=int(env_inference_size) if env_inference_size else 416,
            num_threads=int(env_num_threads) if env_num_threads else min(cpu_count, 8),
            max_fps_target=int(env_target_fps) if env_target_fps else 30,
            confidence_threshold=float(env_confidence) if env_confidence else 0.50,
            model_path=model_path,
            use_int8=use_int8,
            camera_width=int(env_cam_w) if env_cam_w else 1280,
            camera_height=int(env_cam_h) if env_cam_h else 720,
            camera_fps=int(env_cam_fps) if env_cam_fps else 30,
            gpu_memory_mb=512,
            cpu_cores=cpu_count,
            ram_mb=ram_mb,
        )
    
    logger.info(f"Platform detected: {config.platform} ({config.device_name})")
    return config


# ============================================================================
# MAIN / TESTING
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config = get_platform_config()
    print(config)
    
    stats = get_system_stats()
    print("\n📊 System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    cameras = detect_usb_cameras()
    print(f"\n📷 Detected Cameras: {len(cameras)}")
    for cam in cameras:
        print(f"  • {cam['device']} (index: {cam['index']})")
