#!/usr/bin/env python3
"""
Edge Database Connection
SQLite connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import logging

from edge_database.models import Base

logger = logging.getLogger(__name__)


def get_engine(database_url: str = None):
    """Get database engine"""
    if database_url is None:
        db_path = Path(__file__).parent.parent / "data" / "violations.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    
    logger.info(f"Database engine created: {database_url}")
    return engine


def get_session(engine=None):
    """Get database session"""
    if engine is None:
        engine = get_engine()
    
    Session = sessionmaker(bind=engine)
    return Session()
