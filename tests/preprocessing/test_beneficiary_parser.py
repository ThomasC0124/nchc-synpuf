import os
import json
import pytest
import logging

from preprocessing import BeneficiarySummaryParser

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def beneficiary_summary_parser(beneficiary_summary_header_fn):
    parser = BeneficiarySummaryParser(beneficiary_summary_header_fn)
    return parser

def test_instantiate_beneficiary_summary_parser(beneficiary_summary_parser, fake_header_fn):
    assert hasattr(beneficiary_summary_parser, 'ref_header_fn')
    with pytest.raises(AssertionError):
        parser = BeneficiarySummaryParser(fake_header_fn)

def test_beneficiary_summary_parser_method_parse_data(beneficiary_summary_parser,
                                                      sample_beneficiary_summary_data_fns):
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

def test_beneficiary_summary_parser_data_io_on_fake(beneficiary_summary_parser,
                                                    fake_beneficiary_summary_data_fn):
    beneficiary_summary_parser.add_data_file(fake_beneficiary_summary_data_fn)
    # TODO: make sure logging messages are captured
    fn_outs = beneficiary_summary_parser.parse_data()
