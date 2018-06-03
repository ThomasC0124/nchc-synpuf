import os
import pytest

from preprocessing.parser import Parser
from preprocessing.beneficiary import BeneficiarySummaryParser

def test_instantiate_parser(fake_header_fn):
    parser = Parser('./meta_folder/meta_header_ref.json')
    with pytest.raises(AttributeError):
        parser.ref_header_fn = fake_header_fn
    with pytest.raises(NotImplementedError):
        parser.parse_data()

def test_instantiate_beneficiary_summary_parser(beneficiary_summary_header_fn, fake_header_fn):
    parser = BeneficiarySummaryParser(beneficiary_summary_header_fn)
    assert hasattr(parser, 'ref_header_fn')
    with pytest.raises(AssertionError):
        parser = BeneficiarySummaryParser(fake_header_fn)

def test_beneficiary_summary_parser_data_io_on_sample(beneficiary_summary_header_fn,
                                                      sample_beneficiary_summary_data_fn):
    parser = BeneficiarySummaryParser(beneficiary_summary_header_fn)
    parser.add_data_file(sample_beneficiary_summary_data_fn)
    fn_out = './tests/sample_bene_summary.json'
    parser.parse_data(fn_out)
    assert os.path.isfile(fn_out)
    os.remove(fn_out)

def test_beneficiary_summary_parser_data_io_on_fake(beneficiary_summary_header_fn,
                                                    fake_beneficiary_summary_data_fn):
    parser = BeneficiarySummaryParser(beneficiary_summary_header_fn)
    parser.add_data_file(fake_beneficiary_summary_data_fn)
    # TODO: make sure logging messages are generated
    fn_out = './tests/sample_bene_summary.json'
    parser.parse_data(fn_out)
