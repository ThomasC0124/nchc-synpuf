import os
import json
import pytest
import logging

from preprocessing import ClaimParser

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def inpatient_claim_parser():
    parser = ClaimParser('inpatient')
    return parser

def test_instantiation(inpatient_claim_parser):
    for method in ['merge_claim_lines']:
        parser_method = getattr(inpatient_claim_parser, method, None)
        assert callable(parser_method)

def test_inpatient_parse_data(inpatient_claim_parser, sample_inpatient_claim_data_fn):
    inpatient_claim_parser.add_data_file(sample_inpatient_claim_data_fn)
    fn_outs = inpatient_claim_parser.parse_data()
    assert len(fn_outs) == 1
    assert os.path.isfile(fn_outs[0])
    with open(fn_outs[0], 'r') as fp:
        for line in fp:
            line = json.loads(line.strip())
            for k in ['memberID', 'claimID', 'claimLine', 'startDate']:
                assert k in line
    os.remove(fn_outs[0])

def test_inpatient_merge_claim_lines(inpatient_claim_parser, sample_inpatient_claim_data_fn):
    inpatient_claim_parser.add_data_file(sample_inpatient_claim_data_fn)
    fn_outs = inpatient_claim_parser.parse_data()
    for fn_out in fn_outs:
        inpatient_claim_parser.add_data_file(fn_out)
    claims_by_mid = inpatient_claim_parser.merge_claim_lines()
    for mid in ['0005EC02F1DC3A15', '000960C9E1C43BE4', '00098CF15837D918']:
        assert mid in claims_by_mid
    for i, claim in enumerate(claims_by_mid['0005EC02F1DC3A15']):
        if i == 0:
            assert claim['claimID'] == '293491115504906'
        elif i == 1:
            assert claim['claimID'] == '293911115441577'

def test_inpatient_merge_claim_lines_on_wrong_context_format(inpatient_claim_parser,
                                                             sample_inpatient_claim_data_fn):
    inpatient_claim_parser.add_data_file(sample_inpatient_claim_data_fn)
    with pytest.raises(ValueError):
        inpatient_claim_parser.merge_claim_lines()
    os.remove('./temp_claim_lines_to_sort.txt')

@pytest.fixture
def outpatient_claim_parser(outpatient_claim_header_fn):
    parser = ClaimParser('outpatient', outpatient_claim_header_fn)
    return parser
