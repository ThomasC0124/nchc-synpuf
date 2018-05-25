import pytest

from preprocessing.parser import Parser, BeneficiarySummaryParser

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
    parser.open_data_file(sample_beneficiary_summary_data_fn)
    _ = next(parser.data_handle)
    # TODO: change to parser.parse_data(fn_out)
    # TODO: check output file is created at `fn_out`
    parser.close_data_file()
    with pytest.raises(ValueError):
        _ = next(parser.data_handle)    # should not be able to iterate through file since it's closed

def test_beneficiary_summary_parser_data_io_on_fake(beneficiary_summary_header_fn,
                                                    fake_beneficiary_summary_data_fn):
    parser = BeneficiarySummaryParser(beneficiary_summary_header_fn)
    with pytest.raises(IOError):
        parser.open_data_file(fake_beneficiary_summary_data_fn)
    parser.close_data_file()    # do nothing
