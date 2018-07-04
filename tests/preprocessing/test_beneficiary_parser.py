import os
import json
import pytest
import logging

from preprocessing import BeneficiarySummaryParser

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def beneficiary_summary_parser():
    parser = BeneficiarySummaryParser()
    return parser

def test_instantiation(beneficiary_summary_parser):
    for method in ['combine_data']:
        parser_method = getattr(beneficiary_summary_parser, method, None)
        assert callable(parser_method)

def test_parse_data(beneficiary_summary_parser, sample_beneficiary_summary_data_fns):
    for fn_in in sample_beneficiary_summary_data_fns:
        beneficiary_summary_parser.add_data_file(fn_in)
    fn_outs = beneficiary_summary_parser.parse_data()
    assert len(fn_outs) == len(sample_beneficiary_summary_data_fns)
    for fn_out in fn_outs:
        assert os.path.isfile(fn_out)
        with open(fn_out, 'r') as fp:
            for line in fp:
                line = json.loads(line.strip())
                for k in ['memberID', 'gender', 'DOB', 'race']:
                    assert k in line
        os.remove(fn_out)

def test_data_io_on_fake_fn(beneficiary_summary_parser, fake_beneficiary_summary_data_fn):
    beneficiary_summary_parser.add_data_file(fake_beneficiary_summary_data_fn)
    # TODO: make sure logging messages are captured
    fn_outs = beneficiary_summary_parser.parse_data()
