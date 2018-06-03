import json
import logging

from collections import defaultdict
from datetime import datetime

from parser import Parser

class BeneficiarySummaryParser(Parser):
    _fields_change_yearly = set(['ESRDStatus', 'Alzheimer', 'CHF', 'CKD', 'cancer', 'COPD',
                                 'depression', 'diabetes', 'ischemicHD', 'osteoporosis',
                                 'RAOA', 'stroke'])
    def __init__(self, ref_header_fn):
        super(BeneficiarySummaryParser, self).__init__(ref_header_fn)
        self.logger = logging.getLogger('BeneficiarySummaryParser')
        self._load_ref_header()
        assert self._ref_header is not None, self.logger.error('reference header not loaded')

    def parse_data(self, fn_out):
        time_started = datetime.now()
        self._open_data_file()
        if self._data_handle is None:
            self.logger.warning('unable to parse data since data file is not opened')
            return
        parsed_data = {}
        reader = self._create_csv_reader(self._data_handle, ',')
        header = reader.next()
        for raw_line in reader:
            parsed_line = self._parse_raw_line(raw_line, header, self._ref_header)
            member_id = parsed_line.pop('memberID', 'NA')
            if member_id != 'NA':
                parsed_data[member_id] = parsed_line
        time_spent = datetime.now() - time_started
        self.logger.info('time spent parsing: {} seconds'.format(time_spent.total_seconds()))
        time_started = datetime.now()
        with open(fn_out, 'w') as fp_out:
            for member_id, member_doc in parsed_data.iteritems():
                member_doc['memberID'] = member_id
                fp_out.write(json.dumps(member_doc)+'\n')
        self._close_data_file()
        time_spent = datetime.now() - time_started
        self.logger.info('time spent dumping: {} seconds'.format(time_spent.total_seconds()))

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

    def combine_data(self, fn_ins_by_year):
        time_started = datetime.now()
        combined_data = defaultdict(lambda: defaultdict(dict))
        for year, fn_in in fn_ins_by_year.iteritems():
            with open(fn_in, 'r') as fp:
                for member_doc in fp:
                    member_doc = json.loads(member_doc)
                    member_id = member_doc.pop('memberID')
                    for field, val in member_doc.iteritems():
                        if field in self._fields_change_yearly:
                            combined_data[member_id][field][year] = val
                        else:
                            existing_val = combined_data.get(member_id, {}).get(field, '')
                            if val != existing_val:
                                if existing_val != '':
                                    self.logger.warning(
                                        '{}\'s {} changed from {} to {}'.format(
                                            member_id, field, existing_val, val
                                        )
                                    )
                                combined_data[member_id][field] = val
        time_spent = datetime.now() - time_started
        self.logger.info('time spent combining: {} seconds'.format(time_spent.total_seconds()))
        return combined_data
