import os
import pytest
import logging

from preprocessing.beneficiary import BeneficiarySummaryParser

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def beneficiary_summary_parser(beneficiary_summary_header_fn):
    parser = BeneficiarySummaryParser(beneficiary_summary_header_fn)
    return parser

def test_instantiate_beneficiary_summary_parser(beneficiary_summary_parser, fake_header_fn):
    assert hasattr(beneficiary_summary_parser, 'ref_header_fn')
    with pytest.raises(AssertionError):
        parser = BeneficiarySummaryParser(fake_header_fn)

def test_beneficiary_summary_parser_data_io_on_sample(beneficiary_summary_parser,
                                                      sample_beneficiary_summary_data_fn):
    beneficiary_summary_parser.add_data_file(sample_beneficiary_summary_data_fn)
    fn_out = './tests/sample_bene_summary.json'
    beneficiary_summary_parser.parse_data(fn_out)
    assert os.path.isfile(fn_out)
    os.remove(fn_out)

def test_beneficiary_summary_parser_data_io_on_fake(beneficiary_summary_parser,
                                                    fake_beneficiary_summary_data_fn):
    beneficiary_summary_parser.add_data_file(fake_beneficiary_summary_data_fn)
    fn_out = './tests/sample_bene_summary.json'
    beneficiary_summary_parser.parse_data(fn_out)
