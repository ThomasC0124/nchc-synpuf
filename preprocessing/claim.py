import os
import json
import ntpath
import logging
import subprocess

from parser import Parser

SCRIPT_DIR = os.path.dirname(__file__)

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

    def merge_claim_lines(self, fn_ins):
        """Merge *ALL* claim lines in `fn_ins`"""
        temp_fn_claim_lines_to_sort = './temp_claim_lines_to_sort.txt'
        with open(temp_fn_claim_lines_to_sort, 'w') as fp_out:
            for fn_in in fn_ins:
                with open(fn_in, 'r') as fp_in:
                    for claim_line in fp_in:
                        claim_line = json.loads(claim_line)
                        member_id = claim_line.pop('memberID')
                        fp_out.write('{}|{}\n'.format(member_id, claim_line))
        sorting_unix_script_fn = os.path.join(SCRIPT_DIR, 'unix_sort.sh')
        temp_fn_claim_lines_sorted = './temp_claim_lines_sorted.txt'
        subprocess.call(
            [sorting_unix_script_fn, temp_fn_claim_lines_to_sort, temp_fn_claim_lines_sorted]
        )
        os.remove(temp_fn_claim_lines_to_sort)
        merged_claims = self._merge_claim_lines_by_claim_id(temp_fn_claim_lines_sorted)
        return merged_claims

    def _merge_claim_lines_by_claim_id(self, claim_lines_sorted_by_unix):
        """Merge claim lines already sorted by member ID by claim ID"""
        merged_claims = {}
        with open(claim_lines_sorted_by_unix, 'r') as fp_in:
            last_member_id = None
            claim_line_container = []
            for line in fp_in:
                member_id, claim_line = line.split('|')
                if self._to_dump_container(member_id, last_member_id):
                    pass
                    # dump and merge claim lines from claim_line_container here
                    # merged_claims[last_member_id] = claims
                    claim_line_container = []
                claim_line_container.append(claim_line)
                last_member_id = member_id
        if len(claim_line_container) > 0:
            pass
            # dump and merge claim lines from claim_line_container here
            # merged_claims[last_member_id] = claims
        return merged_claims

    def _to_dump_container(self, current_mid, last_mid):
        to_dump = False
        if current_mid != last_mid and last_mid is not None:
            to_dump = True
        return to_dump
