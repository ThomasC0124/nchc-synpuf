import os
import pytest
import logging

from preprocessing.parser import Parser
from preprocessing.beneficiary import BeneficiarySummaryParser
from preprocessing.claim import ClaimParser

logging.basicConfig(level=logging.DEBUG)

def test_instantiate_parser():
    parser = Parser('./meta_folder/meta_header_ref.json')
    for method in ['add_data_file', 'pop_data_file', 'remove_data_file', 'parse_data']:
        parser_method = getattr(parser, method, None)
        assert callable(parser_method)

@pytest.fixture
def parser():
    parser = Parser('./meta_folder/meta_header_ref.json')
    return parser

def test_parser_reassign_reference_header(parser, fake_header_fn):
    with pytest.raises(AttributeError):
        parser.ref_header_fn = fake_header_fn

def test_parser_file_operation(parser):
    fake_data_fn = './rawdata/no_such_data_{}.csv'
    # add and pop one file
    parser.add_data_file(fake_data_fn.format('i'))
    popped_file = parser.pop_data_file()
    assert popped_file == fake_data_fn.format('i')
    # add and pop multiple files
    for k in ['i', 'j']:
        parser.add_data_file(fake_data_fn.format(k))
    _ = parser.pop_data_file()
    popped_file = parser.pop_data_file()
    assert popped_file == fake_data_fn.format('j')
    # pop from empty queue
    popped_file = parser.pop_data_file()
    assert popped_file is None

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

@pytest.fixture
def inpatient_claim_parser(inpatient_claim_header_fn):
    parser = ClaimParser('inpatient', inpatient_claim_header_fn)
    return parser

def test_instantiate_inpatient_claim_parser(inpatient_claim_parser, fake_header_fn):
    assert hasattr(inpatient_claim_parser, 'ref_header_fn')
    with pytest.raises(AssertionError):
        parser = ClaimParser('fake', fake_header_fn)
