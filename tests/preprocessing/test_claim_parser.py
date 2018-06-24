import os
import pytest
import logging

from preprocessing import ClaimParser

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def inpatient_claim_parser(inpatient_claim_header_fn):
    parser = ClaimParser('inpatient', inpatient_claim_header_fn)
    return parser

def test_instantiate_inpatient_claim_parser(inpatient_claim_parser, inpatient_claim_header_fn,
                                            fake_header_fn):
    assert hasattr(inpatient_claim_parser, 'ref_header_fn')
    with pytest.raises(AssertionError):
        parser = ClaimParser('outpatient', inpatient_claim_header_fn)
    with pytest.raises(AssertionError):
        parser = ClaimParser('fake', fake_header_fn)

def test_inpatient_claim_parser_method_parse_data(inpatient_claim_parser):
    assert False

def test_inpatient_claim_parser_method_merge_claim_lines():
    assert False
