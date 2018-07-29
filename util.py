import json
import logging

from logging.handlers import RotatingFileHandler

def configure_logger(logger, log_fn, log_level=logging.INFO, max_bytes=4096, backup_count=3):
    logger.setLevel(log_level)
    handler = RotatingFileHandler(log_fn, maxBytes=max_bytes, backupCount=backup_count)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def save_to_json(data, fn_out):
    with open(fn_out, 'wb') as fp:
        json.dump(data, fp, indent=2)

