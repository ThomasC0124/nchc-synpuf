import csv
import json
import logging

from collections import defaultdict

class Parser(object):
    def __init__(self, ref_header_fn):
        self._ref_header_fn = ref_header_fn
        self._data_handle = None
        self.logger = logging.getLogger('Parser')

    @property
    def ref_header_fn(self):
        return self._ref_header_fn

    @property
    def data_handle(self):
        return self._data_handle

    def open_data_file(self, fn_in):
        self._data_handle = open(fn_in, 'rb')

    def close_data_file(self):
        if self.data_handle:
            self.data_handle.close()

    def parse_data(self):
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

class BeneficiarySummaryParser(Parser):
    def __init__(self, ref_header_fn):
        super(BeneficiarySummaryParser, self).__init__(ref_header_fn)
        self.logger = logging.getLogger('BeneficiarySummaryParser')
        self._load_ref_header()
        assert self._ref_header is not None, self.logger.error('reference header not loaded')

    def parse_data(self, fn_out):
        parsed_data = {}
        reader = self._create_csv_reader(self.data_handle, ',')
        header = reader.next()
        for raw_line in reader:
            parsed_line = self._parse_raw_line(raw_line, header, self._ref_header)
            member_id = parsed_line.pop('memberID', 'NA')
            if member_id != 'NA':
                parsed_data[member_id] = parsed_line
        with open(fn_out, 'w') as fp_out:
            for member_id, member_doc in parsed_data.iteritems():
                member_doc['memberID'] = member_id
                fp_out.write(json.dumps(member_doc)+'\n')

    def _parse_raw_line(self, raw_line, header, ref):
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

    def combine_data(self, fn_in_list):
        # beneficiary_summary = _wrap_up_summary(beneficiary_summary)
        pass

class ClaimParser(Parser):
    def __init__(self, ref_header_fn):
        super(ClaimParser, self).__init__(ref_header_fn)
        self._load_ref_header()
        assert self._ref_header is not None, '[error] reference header not loaded'

    def parse_data(self):
        pass
