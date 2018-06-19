import os
import pytest
import logging

from preprocessing.claim import ClaimParser

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def inpatient_claim_parser(inpatient_claim_header_fn):
    parser = ClaimParser('inpatient', inpatient_claim_header_fn)
    return parser

def test_instantiate_inpatient_claim_parser(inpatient_claim_parser, fake_header_fn):
    assert hasattr(inpatient_claim_parser, 'ref_header_fn')
    with pytest.raises(AssertionError):
        parser = ClaimParser('fake', fake_header_fn)
