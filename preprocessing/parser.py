import csv
import json
import logging

from collections import deque

class Parser(object):
    def __init__(self, ref_header_fn):
        self._ref_header_fn = ref_header_fn
        self._file_queue = deque()
        self._data_handle = None
        self.logger = logging.getLogger('Parser')

    @property
    def ref_header_fn(self):
        return self._ref_header_fn

    def add_data_file(self, fn_in):
        self._file_queue.appendleft(fn_in)

    def pop_data_file(self):
        try:
            data_file = self._file_queue.pop()
            return data_file
        except IndexError as ie:
            self.logger.warning(ie, exc_info=True)

    def remove_data_file(self, fn_in):
        try:
            self._file_queue.remove(fn_in)
        except ValueError as ve:
            self.logger.warning(ve, exc_info=True)

    def _open_data_file(self):
        data_file = self.pop_data_file()
        try:
            self._data_handle = open(data_file, 'rb')
        except TypeError as te: # when `data_file` is None
            self.logger.error(te, exc_info=True)
        except IOError as ioe:  # when `data_file` doesn't exist
            self.logger.error(ioe, exc_info=True)

    def _close_data_file(self):
        if self._data_handle:
            self._data_handle.close()

    def parse_data(self):
        self.logger.warning('attempted to call unimplemented "parse_data" function')
        raise NotImplementedError('"parse_data" function not implemented')

    def _create_csv_reader(self, fp, delimiter):
        reader = csv.reader(fp, delimiter=delimiter)
        return reader

    def _load_ref_header(self):
        self._ref_header = None
        try:
            with open(self.ref_header_fn, 'r') as fp:
                self._ref_header = json.load(fp)
        except IOError as ioe:
            self.logger.error(ioe, exc_info=True)
