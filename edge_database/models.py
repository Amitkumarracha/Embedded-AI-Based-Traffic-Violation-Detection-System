#!/usr/bin/env python3
"""
Edge Database Models
SQLite models for violation storage
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Violation(Base):
    """Violation record"""
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    violation_type = Column(String(50), nullable=False)
    plate_number = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    evidence_path = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Violation(id={self.id}, type={self.violation_type}, plate={self.plate_number})>"
