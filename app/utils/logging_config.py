"""
Structured logging configuration for production
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add source location
        log_record['source'] = f"{record.filename}:{record.lineno}"
        
        # Add function name
        log_record['function'] = record.funcName

def setup_logging(environment: str = "production", log_level: str = "INFO"):
    """
    Setup structured logging
    
    Args:
        environment: "development" or "production"
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if environment == "production":
        # JSON logging for production
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s'
        )
    else:
        # Human-readable logging for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    details: Dict[str, Any] = None,
    severity: str = "info"
):
    """Log security event with structured data"""
    logger = logging.getLogger("security")
    
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "severity": severity,
        "details": details or {}
    }
    
    log_method = getattr(logger, severity.lower(), logger.info)
    log_method(f"Security event: {event_type}", extra=log_data)

def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None,
    ip_address: str = None
):
    """Log API request with structured data"""
    logger = logging.getLogger("api")
    
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "user_id": user_id,
        "ip_address": ip_address
    }
    
    logger.info(f"{method} {path} {status_code}", extra=log_data)

def log_database_query(
    query: str,
    duration_ms: float,
    rows_affected: int = None
):
    """Log database query with structured data"""
    logger = logging.getLogger("database")
    
    log_data = {
        "query": query[:200],  # Truncate long queries
        "duration_ms": duration_ms,
        "rows_affected": rows_affected
    }
    
    logger.debug("Database query executed", extra=log_data)

def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: str = None
):
    """Log error with structured data and context"""
    logger = logging.getLogger("error")
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "user_id": user_id,
        "context": context or {}
    }
    
    logger.error(f"Error occurred: {type(error).__name__}", extra=log_data, exc_info=True)
