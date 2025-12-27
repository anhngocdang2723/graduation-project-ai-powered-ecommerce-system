"""
Centralized logging configuration for Chatbot Multi-Agent System

This module provides structured logging for tracking data flow through:
1. Input Processing (raw message → cleaned input)
2. Intent Classification (input → intent + entities)
3. Orchestration (intent → action plan)
4. Tool Execution (plan → data retrieval)
5. Response Generation (data → final response)

Log Format: [TIMESTAMP] LEVEL [AGENT_NAME] - Message
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file path with timestamp
LOG_FILE = LOGS_DIR / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"

# Custom formatter for structured logging
class AgentFormatter(logging.Formatter):
    """
    Custom formatter that adds color for console and structured format for file
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
            fmt='%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.use_color = use_color
    
    def format(self, record):
        if self.use_color and record.levelname in self.COLORS:
            # Add color to level name for console
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> None:
    """
    Setup logging configuration for the chatbot service
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Write logs to file
        enable_console_logging: Print logs to console
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (with color)
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(AgentFormatter(use_color=True))
        root_logger.addHandler(console_handler)
    
    # File handler (no color)
    if enable_file_logging:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(AgentFormatter(use_color=False))
        root_logger.addHandler(file_handler)
    
    # Reduce verbosity of third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log startup message
    root_logger.info("=" * 80)
    root_logger.info(f"Chatbot Multi-Agent System Logging Initialized")
    root_logger.info(f"Log Level: {log_level}")
    root_logger.info(f"Log File: {LOG_FILE}")
    root_logger.info("=" * 80)


def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get a logger instance for a specific agent
    
    Args:
        agent_name: Name of the agent (e.g., "InputProcessor", "IntentClassifier")
    
    Returns:
        Logger instance configured for the agent
    """
    return logging.getLogger(f"agent.{agent_name}")


# Utility functions for logging data flow
def log_data_flow(logger: logging.Logger, stage: str, input_data: dict, output_data: dict):
    """
    Log data transformation at each stage of the pipeline
    
    Args:
        logger: Logger instance
        stage: Name of the processing stage
        input_data: Input data summary
        output_data: Output data summary
    """
    logger.info(f"[{stage}] INPUT: {input_data}")
    logger.info(f"[{stage}] OUTPUT: {output_data}")


def log_agent_execution(
    logger: logging.Logger, 
    agent_name: str, 
    session_id: str,
    execution_time_ms: Optional[float] = None,
    success: bool = True,
    details: Optional[dict] = None
):
    """
    Log agent execution metrics
    
    Args:
        logger: Logger instance
        agent_name: Name of the agent
        session_id: Session ID for tracking
        execution_time_ms: Time taken to execute
        success: Whether execution was successful
        details: Additional details to log
    """
    status = "SUCCESS" if success else "FAILED"
    msg = f"[{agent_name}] Session={session_id} Status={status}"
    
    if execution_time_ms:
        msg += f" Time={execution_time_ms:.2f}ms"
    
    if details:
        msg += f" Details={details}"
    
    if success:
        logger.info(msg)
    else:
        logger.error(msg)


# Export logging functions
__all__ = [
    'setup_logging',
    'get_agent_logger',
    'log_data_flow',
    'log_agent_execution',
    'LOGS_DIR',
    'LOG_FILE'
]
