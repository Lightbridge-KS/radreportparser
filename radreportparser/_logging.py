# In __init__.py or a new logging.py file
import logging
import sys

def _setup_default_logger():
    """Set up the default logger for radreportparser.
    
    This creates a default configuration that:
    1. Shows warnings and above to stderr
    2. Uses a simple format that's easy to read
    3. Only configures logging for this package, not the root logger
    
    Users can still override this configuration by:
    1. Getting the logger with logging.getLogger('radreportparser')
    2. Removing the default handler with logger.removeHandler()
    3. Adding their own handlers and configuration
    """
    logger = logging.getLogger("radreportparser")
    
    # Only add handler if none exist (avoid duplicate handlers)
    if not logger.handlers:
        # Create default handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s [%(name)s] - %(message)s'))
        
        # Add handler and set level
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
    
    return logger

# Create and configure the default logger
logger = _setup_default_logger()