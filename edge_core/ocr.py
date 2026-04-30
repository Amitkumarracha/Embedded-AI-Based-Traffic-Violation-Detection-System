#!/usr/bin/env python3
"""
Edge-Optimized License Plate OCR
PaddleOCR for Raspberry Pi 5
"""

import cv2
import numpy as np
import logging
import re
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlateResult:
    """OCR result"""
    raw_text: str
    cleaned_text: str
    confidence: float
    is_valid: bool


class EdgeOCR:
    """Lightweight OCR for edge deployment"""
    
    PLATE_REGEX = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$'
    
    def __init__(self):
        self.ocr = None
        logger.info("EdgeOCR initialized (lazy-loaded)")
    
    def _init_ocr(self):
        """Lazy initialization"""
        if self.ocr is not None:
            return
        
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=False, lang='en')
            logger.info("✅ PaddleOCR loaded")
        except ImportError as e:
            logger.error(f"PaddleOCR not available: {e}")
            raise
    
    def read_plate(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[PlateResult]:
        """Extract plate text from frame"""
        if self.ocr is None:
            self._init_ocr()
        
        x1, y1, x2, y2 = bbox
        
        # Add padding
        padding = 10
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(frame.shape[1], x2 + padding)
        y2 = min(frame.shape[0], y2 + padding)
        
        plate_crop = frame[y1:y2, x1:x2]
        
        if plate_crop.shape[0] < 20 or plate_crop.shape[1] < 60:
            return None
        
        # Preprocess
        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        threshold_bgr = cv2.cvtColor(threshold, cv2.COLOR_GRAY2BGR)
        
        try:
            result = self.ocr.ocr(threshold_bgr)
            
            if not result or not result[0]:
                return None
            
            raw_text = result[0][0][1]
            confidence = float(result[0][0][2])
            
            cleaned_text = self._clean_text(raw_text)
            is_valid = bool(re.match(self.PLATE_REGEX, cleaned_text))
            
            return PlateResult(
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                confidence=confidence,
                is_valid=is_valid
            )
        
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean OCR output"""
        cleaned = text.upper().replace(' ', '').replace('-', '')
        
        # Character corrections
        corrections = {'O': '0', 'I': '1', 'S': '5', 'B': '8', 'G': '6'}
        cleaned_list = list(cleaned)
        
        for i, char in enumerate(cleaned_list):
            if 2 <= i < 4 or 6 <= i < 10:  # Numeric positions
                if char in corrections:
                    cleaned_list[i] = corrections[char]
        
        return ''.join(cleaned_list)
