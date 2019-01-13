import csv
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

def load_json(fn_in, multi_lines=False):
    data = {}
    with open(fn_in, 'rb') as fp_in:
        if multi_lines is True:
            for line in fp_in:
                line = json.loads(line.strip())
                member_id = line.pop('memberID')
                data[member_id] = line
        else:
            data = json.load(fp_in)
    return data

def load_csv(fn_in):
    header = []
    matrix = []
    with open(fn_in, 'rb') as fp_in:
        reader = csv.reader(fp_in)
        header = next(reader)
        for line in reader:
            matrix.append(line)
    return header, matrix
