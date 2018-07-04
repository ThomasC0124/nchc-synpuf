import os
import csv
import json
import logging

from collections import deque, defaultdict

class Parser(object):
    def __init__(self):
        self._ref_header = None
        self._file_queue = deque()
        self._data_handle = None
        self.logger = logging.getLogger('Parser')

    def add_data_file(self, fn_in):
        """Left-append `fn_in` to the processing queue"""
        self._file_queue.appendleft(fn_in)

    def pop_data_file(self):
        """Pop out the right-most file name from the processing queue"""
        try:
            data_file = self._file_queue.pop()
            return data_file
        except IndexError as ie:
            self.logger.warning(ie, exc_info=True)

    def remove_data_file(self, fn_in):
        """Remove `fn_in` from the processing queue"""
        try:
            self._file_queue.remove(fn_in)
        except ValueError as ve:
            self.logger.warning(ve, exc_info=True)

    def _open_data_file(self, data_file):
        """Try to open `data_file` and assign it to self._data_handle"""
        try:
            self._data_handle = open(data_file, 'rb')
        except TypeError as te: # when `data_file` is None
            self.logger.error(te, exc_info=True)
        except IOError as ioe:  # when `data_file` doesn't exist
            self.logger.error(ioe, exc_info=True)

    def _close_data_file(self):
        """Close the buffer self._data_handle"""
        if self._data_handle:
            self._data_handle.close()
            self._data_handle = None

    def parse_data(self):
        """Parse the data files stored in self._file_queue and return a list of parsed file names"""
        parsed_files = []
        while len(self._file_queue) > 0:
            next_data_file = self.pop_data_file()
            self._open_data_file(next_data_file)
            if self._data_handle is None:
                self.logger.warning('unable to parse data since data file is not opened')
                return
            if self._ref_header is None:
                self.logger.warning(
                    'unable to parse data since the reference header has not yet been loaded'
                )
            parsed_data = defaultdict(list)
            reader = self._create_csv_reader(self._data_handle, ',')
            header = reader.next()
            for raw_line in reader:
                parsed_line = self._parse_raw_line(raw_line, header, self._ref_header)
                member_id = parsed_line.pop('memberID', 'NA')
                if member_id != 'NA':
                    parsed_data[member_id].append(parsed_line)
            filename, ext = os.path.splitext(next_data_file)
            fn_out = '{}_parsed{}'.format(filename, ext)
            with open(fn_out, 'w') as fp_out:
                for member_id, member_docs in parsed_data.iteritems():
                    for member_doc in member_docs:
                        member_doc['memberID'] = member_id
                        fp_out.write(json.dumps(member_doc)+'\n')
            parsed_files.append(fn_out)
            self._close_data_file()
        return parsed_files

    def _parse_raw_line(self, raw_line, header, ref):
        """Parse single list-like `raw_line` into dictionary according to `header` and `ref`"""
        parsed_line = defaultdict(list)
        for field in ref:
            field_ref_doc = ref[field]
            if isinstance(field_ref_doc['origName'], list):
                for raw_field_name in field_ref_doc['origName']:
                    value = raw_line[header.index(raw_field_name)]
                    if 'valueMap' in field_ref_doc:
                        value = field_ref_doc['valueMap'].get(value, '')
                    if value != '':
                        parsed_line[field].append(value)
            elif isinstance(field_ref_doc['origName'], unicode):
                value = raw_line[header.index(field_ref_doc['origName'])]
                if 'valueMap' in field_ref_doc:
                    value = field_ref_doc['valueMap'].get(value, '')
                if value != '':
                    parsed_line[field] = value
        return parsed_line

    def _create_csv_reader(self, fp, delimiter):
        """Add CSV reader buffer onto `fp`"""
        reader = csv.reader(fp, delimiter=delimiter)
        return reader
