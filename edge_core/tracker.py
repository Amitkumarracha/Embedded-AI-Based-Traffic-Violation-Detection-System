#!/usr/bin/env python3
"""
Edge-Optimized Vehicle Tracker
Lightweight DeepSort tracker for Raspberry Pi 5
"""

import numpy as np
from typing import List, Tuple, Dict
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False
    logger.warning("deep-sort-realtime not available")


class EdgeTracker:
    """Lightweight vehicle tracker for edge deployment"""
    
    def __init__(self, max_age: int = 30, n_init: int = 3):
        if not DEEPSORT_AVAILABLE:
            raise RuntimeError("deep-sort-realtime is required")
        
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            nms_max_overlap=0.5,
            embedder="mobilenet",
            embedder_gpu=False,
        )
        
        self.track_history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=30))
        self.track_metadata: Dict[int, dict] = {}
        
        logger.info(f"✅ EdgeTracker initialized (max_age={max_age}, n_init={n_init})")
    
    def update(self, detections: List, frame: np.ndarray) -> List:
        """Update tracker with new detections"""
        detections_ds = []
        detection_classes = {}
        
        for idx, det in enumerate(detections):
            w = det.x2 - det.x1
            h = det.y2 - det.y1
            bbox = [det.x1, det.y1, w, h]
            
            detections_ds.append((bbox, det.confidence, det.class_id))
            detection_classes[idx] = (det.class_id, det.class_name, det.confidence)
        
        tracks = self.tracker.update_tracks(detections_ds, frame=frame)
        
        tracked_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            bbox = track.to_ltrb()
            x1, y1, x2, y2 = map(int, bbox)
            
            track_id = track.track_id
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            
            self.track_history[track_id].append((cx, cy))
            
            tracked_objects.append({
                'track_id': track_id,
                'bbox': (x1, y1, x2, y2),
                'center': (cx, cy),
                'class_id': 0,
                'class_name': 'vehicle',
                'confidence': 0.9,
            })
        
        return tracked_objects
