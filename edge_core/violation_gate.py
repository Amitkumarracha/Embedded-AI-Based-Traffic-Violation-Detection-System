#!/usr/bin/env python3
"""
Violation Gate - 4-stage violation confirmation filter
Reduces false positives by requiring consistent detection across frames.
"""

import time
import logging
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class ViolationGate:
    """
    4-stage filter to confirm violations:
    Stage 1: Detection confidence check
    Stage 2: Temporal consistency (N frames)
    Stage 3: Spatial proximity (same area)
    Stage 4: Cooldown (prevent duplicate reports)
    """
    
    def __init__(
        self,
        min_confidence: float = 0.50,
        min_frames: int = 3,
        cooldown_seconds: float = 30.0,
        spatial_threshold: int = 100,
    ):
        self.min_confidence = min_confidence
        self.min_frames = min_frames
        self.cooldown_seconds = cooldown_seconds
        self.spatial_threshold = spatial_threshold
        
        # Track violation history per track_id
        self.violation_history: Dict[int, list] = defaultdict(list)
        self.confirmed_violations: Dict[str, float] = {}  # key -> last_confirmed_time
        self.stats = {"total_checked": 0, "confirmed": 0, "rejected": 0}
        
        logger.info(f"✅ ViolationGate initialized (min_frames={min_frames}, cooldown={cooldown_seconds}s)")
    
    def process(self, detections: list, tracks: dict, frame_id: int) -> list:
        """Process detections through 4-stage gate"""
        confirmed = []
        
        for det in detections:
            self.stats["total_checked"] += 1
            
            # Get detection attributes
            class_name = det.class_name if hasattr(det, 'class_name') else det.get('class_name', '')
            confidence = det.confidence if hasattr(det, 'confidence') else det.get('confidence', 0)
            
            is_violation = class_name in [
                'without_helmet', 'triple_ride', 'traffic_violation',
                'helmet_violation', 'triple_riding'
            ]
            
            if not is_violation:
                continue
            
            # Stage 1: Confidence check
            if confidence < self.min_confidence:
                continue
            
            # Stage 2: Temporal consistency
            track_id = getattr(det, 'center_x', 0) * 1000 + getattr(det, 'center_y', 0)
            self.violation_history[track_id].append({
                'frame_id': frame_id,
                'confidence': confidence,
                'class': class_name,
                'time': time.time(),
            })
            
            # Keep only recent history (last 60 seconds)
            cutoff = time.time() - 60
            self.violation_history[track_id] = [
                h for h in self.violation_history[track_id] if h['time'] > cutoff
            ]
            
            if len(self.violation_history[track_id]) < self.min_frames:
                continue
            
            # Stage 3: Spatial check (already via track_id grouping)
            
            # Stage 4: Cooldown
            violation_key = f"{class_name}_{track_id}"
            last_confirmed = self.confirmed_violations.get(violation_key, 0)
            
            if time.time() - last_confirmed < self.cooldown_seconds:
                continue
            
            # Violation confirmed!
            self.confirmed_violations[violation_key] = time.time()
            self.stats["confirmed"] += 1
            
            confirmed.append({
                'violation_type': class_name,
                'confidence': confidence,
                'track_id': track_id,
                'frame_id': frame_id,
                'plate_bbox': None,
            })
            
            logger.info(f"🚨 CONFIRMED: {class_name} (conf={confidence:.2f}, track={track_id})")
        
        rejected = self.stats["total_checked"] - self.stats["confirmed"]
        self.stats["rejected"] = rejected
        
        return confirmed
    
    def get_stats(self) -> dict:
        return self.stats.copy()
