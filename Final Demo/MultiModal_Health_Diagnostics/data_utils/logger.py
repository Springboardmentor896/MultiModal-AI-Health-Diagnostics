import logging
import sys
from pathlib import Path

# Create logs directory if needed
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """Get configured logger for module."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Avoid duplicate handlers
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        
        # File handler
        file_handler = logging.FileHandler(LOG_DIR / "app.log")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# Quick test
if __name__ == "__main__":
    test_logger = get_logger("test")
    test_logger.info("Logger initialized successfully!")
