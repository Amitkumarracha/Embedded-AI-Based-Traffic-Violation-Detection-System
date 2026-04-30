#!/usr/bin/env python3
"""
YOLO Traffic Violation Detector - Edge Optimized
ONNX-based inference for Raspberry Pi 5 with INT8 support.
Falls back to PyTorch (.pt) if ONNX model is not available.
"""

import numpy as np
import time
import os
import logging
from typing import List, Tuple, NamedTuple, Optional
from pathlib import Path
import cv2

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

CLASS_NAMES = [
    "with_helmet",
    "without_helmet",
    "number_plate",
    "riding",
    "triple_ride",
    "traffic_violation",
    "motorcycle",
    "vehicle",
]

CLASS_COLORS = {
    "with_helmet": (0, 255, 0),
    "without_helmet": (0, 0, 255),
    "number_plate": (0, 255, 255),
    "riding": (255, 0, 0),
    "triple_ride": (0, 165, 255),
    "traffic_violation": (0, 0, 255),
    "motorcycle": (255, 255, 0),
    "vehicle": (128, 0, 128),
}

DANGER_CLASSES = {"without_helmet", "triple_ride", "traffic_violation"}


class Detection(NamedTuple):
    """Single detection result"""
    class_id: int
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    center_x: int
    center_y: int
    width: int
    height: int
    is_danger: bool


# ============================================================================
# DETECTOR (supports both ONNX and PyTorch)
# ============================================================================

class Detector:
    """
    Traffic Violation Detector optimized for edge deployment.
    Supports ONNX (preferred for RPi) and PyTorch (.pt) models.
    """

    def __init__(
        self,
        model_path: str,
        inference_size: int = 320,
        num_threads: int = 4,
        confidence_threshold: float = 0.50,
        providers: Optional[List[str]] = None,
    ):
        self.model_path = str(Path(model_path).expanduser().resolve())
        self.inference_size = inference_size
        self.num_threads = num_threads
        self.confidence_threshold = confidence_threshold
        self.use_onnx = False
        self.use_ultralytics = False
        self.session = None
        self.model = None
        
        if not Path(self.model_path).exists():
            # Try alternative paths
            alt_paths = [
                Path(__file__).parent.parent / "models" / "best.onnx",
                Path(__file__).parent.parent / "models" / "best.pt",
                Path(__file__).parent.parent / "models" / "best_int8.onnx",
            ]
            for alt in alt_paths:
                if alt.exists():
                    self.model_path = str(alt)
                    logger.info(f"Using alternative model: {alt}")
                    break
            else:
                raise FileNotFoundError(
                    f"Model not found: {model_path}\n"
                    f"Place model weights in: {Path(__file__).parent.parent / 'models'}"
                )
        
        # Load model based on file extension
        if self.model_path.endswith('.onnx'):
            self._load_onnx(providers)
        else:
            self._load_ultralytics()
        
        # Warmup
        logger.info("🔥 Warming up model...")
        self._warmup()
        logger.info("✅ Detector ready")
    
    def _load_onnx(self, providers=None):
        """Load ONNX model for inference"""
        try:
            import onnxruntime as ort
            
            if providers is None:
                providers = ["CPUExecutionProvider"]
            
            session_options = ort.SessionOptions()
            session_options.intra_op_num_threads = self.num_threads
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            
            self.session = ort.InferenceSession(
                self.model_path,
                session_options,
                providers=providers,
            )
            
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            self.use_onnx = True
            
            logger.info(f"✅ ONNX model loaded: {Path(self.model_path).name}")
            logger.info(f"   Providers: {self.session.get_providers()}")
            logger.info(f"   Threads: {self.num_threads}")
            
        except ImportError:
            logger.warning("onnxruntime not available, falling back to PyTorch")
            self._load_ultralytics()
    
    def _load_ultralytics(self):
        """Load PyTorch model via Ultralytics"""
        try:
            # Disable weights_only for compatibility
            os.environ['TORCH_LOAD_WEIGHTS_ONLY'] = '0'
            
            import torch
            original_load = torch.load
            def patched_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            torch.load = patched_load
            
            from ultralytics import YOLO
            
            self.model = YOLO(self.model_path)
            self.model.to('cpu')
            self.use_ultralytics = True
            
            torch.load = original_load
            
            logger.info(f"✅ PyTorch model loaded: {Path(self.model_path).name}")
            if hasattr(self.model, 'names'):
                logger.info(f"   Classes: {self.model.names}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def _warmup(self, n_warmup: int = 3):
        """Warmup with dummy input"""
        dummy = np.random.randint(0, 256, (self.inference_size, self.inference_size, 3), dtype=np.uint8)
        for _ in range(n_warmup):
            try:
                self.infer(dummy)
            except Exception:
                pass
    
    def preprocess(self, frame: np.ndarray) -> Tuple[np.ndarray, float, int, int]:
        """Letterbox preprocessing for ONNX inference"""
        h, w = frame.shape[:2]
        scale = min(self.inference_size / w, self.inference_size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        pad_left = (self.inference_size - new_w) // 2
        pad_top = (self.inference_size - new_h) // 2
        
        padded = cv2.copyMakeBorder(
            resized,
            pad_top, self.inference_size - new_h - pad_top,
            pad_left, self.inference_size - new_w - pad_left,
            cv2.BORDER_CONSTANT, value=(128, 128, 128),
        )
        
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        tensor = normalized.transpose(2, 0, 1)[np.newaxis, :, :, :].astype(np.float32)
        
        return tensor, scale, pad_top, pad_left
    
    def infer(self, frame: np.ndarray) -> List[Detection]:
        """Run inference and return detections"""
        if self.use_onnx:
            return self._infer_onnx(frame)
        else:
            return self._infer_ultralytics(frame)
    
    def _infer_onnx(self, frame: np.ndarray) -> List[Detection]:
        """ONNX inference path"""
        h, w = frame.shape[:2]
        tensor, scale, pad_top, pad_left = self.preprocess(frame)
        
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: tensor},
        )
        
        predictions = outputs[0][0]
        detections = []
        
        for pred in predictions:
            class_id, x_c, y_c, w_n, h_n, conf = pred
            
            if conf < self.confidence_threshold:
                continue
            
            class_id = int(class_id)
            if class_id >= len(CLASS_NAMES):
                continue
            
            class_name = CLASS_NAMES[class_id]
            
            x_c_px = (x_c * self.inference_size - pad_left) / scale
            y_c_px = (y_c * self.inference_size - pad_top) / scale
            w_px = w_n * self.inference_size / scale
            h_px = h_n * self.inference_size / scale
            
            x1 = max(0, int(x_c_px - w_px / 2))
            y1 = max(0, int(y_c_px - h_px / 2))
            x2 = min(w, int(x_c_px + w_px / 2))
            y2 = min(h, int(y_c_px + h_px / 2))
            
            detections.append(Detection(
                class_id=class_id, class_name=class_name,
                confidence=float(conf),
                x1=x1, y1=y1, x2=x2, y2=y2,
                center_x=int(x_c_px), center_y=int(y_c_px),
                width=int(w_px), height=int(h_px),
                is_danger=class_name in DANGER_CLASSES,
            ))
        
        return detections
    
    def _infer_ultralytics(self, frame: np.ndarray) -> List[Detection]:
        """Ultralytics/PyTorch inference path"""
        h, w = frame.shape[:2]
        
        results = self.model(
            frame,
            device='cpu',
            conf=self.confidence_threshold,
            imgsz=self.inference_size,
            verbose=False,
        )
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = result.names.get(cls_id, f"class_{cls_id}")
                
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                bw = int(x2 - x1)
                bh = int(y2 - y1)
                
                is_danger = cls_name in DANGER_CLASSES or cls_name in [
                    "without_helmet", "triple_riding", "helmet_violation"
                ]
                
                detections.append(Detection(
                    class_id=cls_id, class_name=cls_name,
                    confidence=conf,
                    x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2),
                    center_x=cx, center_y=cy,
                    width=bw, height=bh,
                    is_danger=is_danger,
                ))
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection],
                        line_thickness: int = 2) -> np.ndarray:
        """Draw bounding boxes on frame"""
        annotated = frame.copy()
        
        for det in detections:
            color = CLASS_COLORS.get(det.class_name, (255, 255, 255))
            
            cv2.rectangle(annotated, (det.x1, det.y1), (det.x2, det.y2), color, line_thickness)
            
            label = f"{det.class_name} {det.confidence:.2f}"
            (lw, lh), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            cv2.rectangle(annotated,
                          (det.x1, det.y1 - lh - baseline),
                          (det.x1 + lw, det.y1), color, -1)
            cv2.putText(annotated, label, (det.x1, det.y1 - baseline),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if det.is_danger:
                cv2.circle(annotated, (det.center_x, det.center_y), 4, (0, 0, 255), -1)
        
        return annotated
    
    def benchmark(self, n_frames: int = 100) -> dict:
        """Benchmark inference performance"""
        dummy = np.random.randint(0, 256, (self.inference_size, self.inference_size, 3), dtype=np.uint8)
        
        # Warmup
        for _ in range(5):
            self.infer(dummy)
        
        times = []
        for _ in range(n_frames):
            start = time.time()
            self.infer(dummy)
            times.append((time.time() - start) * 1000)
        
        times = np.array(times)
        results = {
            "n_frames": n_frames,
            "mean_ms": float(np.mean(times)),
            "median_ms": float(np.median(times)),
            "min_ms": float(np.min(times)),
            "max_ms": float(np.max(times)),
            "fps": float(1000.0 / np.mean(times)),
        }
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    detector = Detector(
        model_path="models/best.onnx",
        inference_size=320,
        num_threads=4,
    )
    
    results = detector.benchmark(n_frames=50)
    print(f"\n📊 Benchmark: {results['mean_ms']:.1f} ms/frame ({results['fps']:.1f} FPS)")
