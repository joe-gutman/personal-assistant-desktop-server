import logging
import os

class SimplifiedNameFormater(logging.Formatter):
    def format(self, record):
        # Simplify the module name to just the last part after the last dot
        if '.' in record.name:
            record.name = record.name.split('.')[-1]
            if len(record.name) > 2:
                record.name += record.name.split('.')[-2:]
            else:
                record.name = record.name.split('.')[-1]
        return super().format(record)

def setup_logging(log_dir="logs", level=logging.DEBUG):
    os.makedirs(log_dir, exist_ok=True)

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formatter = logging.Formatter(log_format)

    file_handler = logging.FileHandler(f"{log_dir}/app.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("quart").setLevel(logging.INFO)