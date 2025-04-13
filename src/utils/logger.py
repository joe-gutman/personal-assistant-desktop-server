import logging
import os
import sys
from logging.handlers import RotatingFileHandler
import codecs
import glob

class UTF8Formatter(logging.Formatter):
    def format(self, record):
        return super().format(record).encode('utf-8').decode('utf-8')

def setup_logger(name, file='app.log', level="INFO", terminal=False):
    # Ensure the logs directory exists
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    file_path = os.path.join(logs_dir, file)

    # Clear the log file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete any extra log files
    log_pattern = file_path + '.*'
    for log_file in glob.glob(log_pattern):
        os.remove(log_file)

    # Create a formatter for consistent log formatting
    formatter = UTF8Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler for writing logs to a file (with rotation and UTF-8 encoding)
    file_handler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8', errors='replace')
    file_handler.setFormatter(formatter)

    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)

    # Console handler for writing logs to the terminal (with UTF-8 encoding)
    if terminal:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Set console encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
