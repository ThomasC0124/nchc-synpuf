import pytest
import logging

from preprocessing.parser import Parser

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
