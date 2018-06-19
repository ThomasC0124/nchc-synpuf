import ntpath
import logging

from datetime import datetime

from parser import Parser

class ClaimParser(Parser):
    _type_header_map = {
        'inpatient': 'inpatientClaimHeader.json',
        'outpatient': 'outpatientClaimHeader.json',
        'carrier': 'carrierClaimHeader.json',
        'pde': 'prescriptionDrugEventHeader.json'
    }
    def __init__(self, parser_type, ref_header_fn):
        super(ClaimParser, self).__init__(ref_header_fn)
        self.logger = logging.getLogger('ClaimParser')
        self._check_types(parser_type, ref_header_fn)
        self._type = parser_type
        self._load_ref_header()
        assert self._ref_header is not None, self.logger.error('reference header not loaded')

    def _check_types(self, parser_type, ref_header_fn):
        """Make sure `parser_type` is supported and correct file name is provided"""
        assert parser_type in self._type_header_map, self.logger.error(
            'parser type {} not available'.format(parser_type)
        )
        header_fn = ntpath.basename(ref_header_fn)
        assert header_fn == self._type_header_map[parser_type], self.logger.error(
            'parser type {} does not match header type {}'.format(parser_type, header_fn)
        )

    def merge_claim_lines(self):
        raise NotImplementedError
