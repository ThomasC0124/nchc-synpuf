import os
import json
import logging

from collections import defaultdict

from parser import Parser
from resource import beneficiary_summary_header

class BeneficiarySummaryParser(Parser):
    _fields_change_yearly = set(['ESRDStatus', 'Alzheimer', 'CHF', 'CKD', 'cancer', 'COPD',
                                 'depression', 'diabetes', 'ischemicHD', 'osteoporosis',
                                 'RAOA', 'stroke'])

    def __init__(self):
        super(BeneficiarySummaryParser, self).__init__()
        self.logger = logging.getLogger('BeneficiarySummaryParser')
        self._load_header()
        assert self._ref_header is not None, self.logger.error('reference header not loaded')

    def _load_header(self):
        """Load JSON-like reference header"""
        self._ref_header = beneficiary_summary_header

    def combine_data(self, fn_ins_by_year):
        """Group `fn_ins_by_year` by member ID to create member-level summary"""
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
            os.remove(fn_in)
        return combined_data
