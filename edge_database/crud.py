#!/usr/bin/env python3
"""
Edge Database CRUD Operations
"""

from datetime import datetime
from typing import List, Optional
import logging

from edge_database.models import Violation
from edge_database.connection import get_session

logger = logging.getLogger(__name__)


def save_violation(
    violation_type: str,
    plate_number: Optional[str] = None,
    confidence: float = 0.0,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    evidence_path: Optional[str] = None
) -> int:
    """Save violation to database"""
    try:
        session = get_session()
        
        violation = Violation(
            violation_type=violation_type,
            plate_number=plate_number,
            confidence=confidence,
            latitude=latitude,
            longitude=longitude,
            evidence_path=evidence_path,
            timestamp=datetime.utcnow()
        )
        
        session.add(violation)
        session.commit()
        
        violation_id = violation.id
        session.close()
        
        logger.info(f"Violation saved: ID={violation_id}, type={violation_type}")
        return violation_id
    
    except Exception as e:
        logger.error(f"Failed to save violation: {e}")
        return -1


def get_violations(limit: int = 100) -> List[Violation]:
    """Get recent violations"""
    try:
        session = get_session()
        violations = session.query(Violation).order_by(Violation.timestamp.desc()).limit(limit).all()
        session.close()
        return violations
    except Exception as e:
        logger.error(f"Failed to get violations: {e}")
        return []


def get_violation_count() -> int:
    """Get total violation count"""
    try:
        session = get_session()
        count = session.query(Violation).count()
        session.close()
        return count
    except Exception as e:
        logger.error(f"Failed to get violation count: {e}")
        return 0
