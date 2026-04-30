#!/usr/bin/env python3
"""
Storage Manager for Limited SSD Space
Automatically manages disk space on 10GB SSD
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import shutil

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages storage on limited SSD space"""
    
    def __init__(self, max_storage_mb: int = 8000):
        """
        Initialize storage manager
        
        Args:
            max_storage_mb: Maximum storage to use in MB (default 8GB of 10GB SSD)
        """
        self.max_storage_bytes = max_storage_mb * 1024 * 1024
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.evidence_dir = self.data_dir / "evidence"
        self.logs_dir = self.project_root / "logs"
        
        logger.info(f"StorageManager initialized (max: {max_storage_mb}MB)")
    
    def get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        try:
            for entry in directory.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception as e:
            logger.error(f"Error calculating directory size: {e}")
        return total
    
    def get_disk_usage(self) -> dict:
        """Get current disk usage statistics"""
        try:
            total, used, free = shutil.disk_usage(self.project_root)
            
            evidence_size = self.get_directory_size(self.evidence_dir) if self.evidence_dir.exists() else 0
            logs_size = self.get_directory_size(self.logs_dir) if self.logs_dir.exists() else 0
            
            return {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'evidence_mb': round(evidence_size / (1024**2), 2),
                'logs_mb': round(logs_size / (1024**2), 2),
                'free_percent': round((free / total) * 100, 1)
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}
    
    def cleanup_old_evidence(self, days: int = 7):
        """Delete evidence images older than N days"""
        if not self.evidence_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        deleted_size = 0
        
        try:
            for file_path in self.evidence_dir.rglob('*.jpg'):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old evidence images ({deleted_size / (1024**2):.2f} MB)")
        
        except Exception as e:
            logger.error(f"Error cleaning up evidence: {e}")
        
        return deleted_count
    
    def cleanup_old_logs(self, days: int = 7):
        """Delete log files older than N days"""
        if not self.logs_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        try:
            for file_path in self.logs_dir.rglob('*.log'):
                if file_path.name == 'edge_system.log':
                    continue  # Keep current log
                
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log files")
        
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
        
        return deleted_count
    
    def rotate_current_log(self):
        """Rotate current log file if it's too large (>10MB)"""
        current_log = self.logs_dir / "edge_system.log"
        
        if not current_log.exists():
            return
        
        try:
            if current_log.stat().st_size > 10 * 1024 * 1024:  # 10MB
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rotated_log = self.logs_dir / f"edge_system_{timestamp}.log"
                current_log.rename(rotated_log)
                logger.info(f"Rotated log file to {rotated_log.name}")
        
        except Exception as e:
            logger.error(f"Error rotating log: {e}")
    
    def check_and_cleanup(self):
        """Check disk space and cleanup if needed"""
        usage = self.get_disk_usage()
        
        if not usage:
            return
        
        logger.info(f"Disk usage: {usage['used_gb']:.2f}GB / {usage['total_gb']:.2f}GB ({usage['free_percent']:.1f}% free)")
        
        # If less than 1GB free, aggressive cleanup
        if usage['free_gb'] < 1.0:
            logger.warning("Low disk space! Running aggressive cleanup...")
            self.cleanup_old_evidence(days=3)
            self.cleanup_old_logs(days=3)
        
        # If less than 2GB free, normal cleanup
        elif usage['free_gb'] < 2.0:
            logger.info("Running normal cleanup...")
            self.cleanup_old_evidence(days=7)
            self.cleanup_old_logs(days=7)
        
        # Rotate log if needed
        self.rotate_current_log()
    
    def get_storage_report(self) -> str:
        """Get formatted storage report"""
        usage = self.get_disk_usage()
        
        if not usage:
            return "Storage information unavailable"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          STORAGE REPORT                                      ║
╠══════════════════════════════════════════════════════════════╣
║  Total Disk:      {usage['total_gb']:.2f} GB                              ║
║  Used:            {usage['used_gb']:.2f} GB                              ║
║  Free:            {usage['free_gb']:.2f} GB ({usage['free_percent']:.1f}% free)              ║
╠──────────────────────────────────────────────────────────────╣
║  Evidence Images: {usage['evidence_mb']:.2f} MB                           ║
║  Log Files:       {usage['logs_mb']:.2f} MB                           ║
╚══════════════════════════════════════════════════════════════╝
"""
        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = StorageManager(max_storage_mb=8000)
    print(manager.get_storage_report())
    
    print("\nRunning cleanup check...")
    manager.check_and_cleanup()
    
    print("\nAfter cleanup:")
    print(manager.get_storage_report())
