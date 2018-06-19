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

    def combine_data(self, fn_ins_by_year):
        """Group `fn_ins_by_year` by member ID to create member-level summary"""
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
