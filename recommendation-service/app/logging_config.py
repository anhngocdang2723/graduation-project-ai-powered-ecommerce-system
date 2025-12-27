"""
Centralized logging configuration for Recommendation Service

This module provides structured logging for tracking recommendation flow:
1. Interaction Tracking (user actions → database)
2. User Profile Building (interactions → preferences)
3. Recommendation Generation (preferences → recommendations)
4. Algorithm Selection (context → strategy)

Log Format: [TIMESTAMP] LEVEL [COMPONENT] - Message
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file path with timestamp
LOG_FILE = LOGS_DIR / f"recommendation_{datetime.now().strftime('%Y%m%d')}.log"


class RecommendationFormatter(logging.Formatter):
    """
    Custom formatter for recommendation service with color support
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def __init__(self, use_color: bool = False):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.use_color = use_color
    
    def format(self, record):
        if self.use_color and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> None:
    """
    Setup logging configuration for recommendation service
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Write logs to file
        enable_console_logging: Print logs to console
    """
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    
    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(RecommendationFormatter(use_color=True))
        root_logger.addHandler(console_handler)
    
    # File handler
    if enable_file_logging:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(RecommendationFormatter(use_color=False))
        root_logger.addHandler(file_handler)
    
    # Reduce verbosity of third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    root_logger.info("=" * 80)
    root_logger.info("Recommendation Service Logging Initialized")
    root_logger.info(f"Log Level: {log_level}")
    root_logger.info(f"Log File: {LOG_FILE}")
    root_logger.info("=" * 80)


def get_rec_logger(component: str) -> logging.Logger:
    """
    Get logger for a recommendation component
    
    Args:
        component: Name of component (e.g., "engine", "tracker", "api")
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"rec.{component}")


def log_interaction(
    logger: logging.Logger,
    user_id: str,
    interaction_type: str,
    product_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Log user interaction tracking
    
    Args:
        logger: Logger instance
        user_id: User ID
        interaction_type: Type of interaction (view, add_to_cart, etc.)
        product_id: Product ID involved
        metadata: Additional metadata
    """
    msg = f"TRACK | User={user_id} Type={interaction_type}"
    if product_id:
        msg += f" Product={product_id}"
    if metadata:
        msg += f" Meta={metadata}"
    logger.info(msg)


def log_recommendation_request(
    logger: logging.Logger,
    user_id: str,
    context: str,
    limit: int,
    filters: Optional[Dict[str, Any]] = None
):
    """
    Log recommendation request
    
    Args:
        logger: Logger instance
        user_id: User ID requesting recommendations
        context: Context of request (homepage, product_page, etc.)
        limit: Number of recommendations requested
        filters: Any filters applied
    """
    msg = f"REQUEST | User={user_id} Context={context} Limit={limit}"
    if filters:
        msg += f" Filters={filters}"
    logger.info(msg)


def log_recommendation_result(
    logger: logging.Logger,
    user_id: str,
    algorithm: str,
    count: int,
    execution_time_ms: float,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log recommendation generation result
    
    Args:
        logger: Logger instance
        user_id: User ID
        algorithm: Algorithm used
        count: Number of recommendations generated
        execution_time_ms: Execution time
        details: Additional details (e.g., source breakdown)
    """
    msg = f"RESULT | User={user_id} Algo={algorithm} Count={count} Time={execution_time_ms:.2f}ms"
    if details:
        msg += f" Details={details}"
    logger.info(msg)


def log_algorithm_selection(
    logger: logging.Logger,
    user_id: str,
    selected_algorithm: str,
    reason: str,
    user_stats: Optional[Dict[str, Any]] = None
):
    """
    Log algorithm selection decision
    
    Args:
        logger: Logger instance
        user_id: User ID
        selected_algorithm: Selected algorithm name
        reason: Reason for selection
        user_stats: User statistics that influenced decision
    """
    msg = f"ALGO_SELECT | User={user_id} Selected={selected_algorithm} Reason={reason}"
    if user_stats:
        msg += f" Stats={user_stats}"
    logger.info(msg)


# Export logging functions
__all__ = [
    'setup_logging',
    'get_rec_logger',
    'log_interaction',
    'log_recommendation_request',
    'log_recommendation_result',
    'log_algorithm_selection',
    'LOGS_DIR',
    'LOG_FILE'
]
