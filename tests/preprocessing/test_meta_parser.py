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

def test_reassign_reference_header(parser, fake_header_fn):
    with pytest.raises(AttributeError):
        parser.ref_header_fn = fake_header_fn

def test_add_data_file(parser):
    fake_data_fn = './rawdata/no_such_data_{}.csv'
    parser.add_data_file(fake_data_fn.format('i'))
    assert fake_data_fn.format('i') in parser._file_queue

def test_pop_data_file(parser):
    # pop from empty queue
    popped_file = parser.pop_data_file()
    assert popped_file is None
    # data popping normal operation
    fake_data_fn = './rawdata/no_such_data_{}.csv'
    for v in ['i', 'j', 'k']:
        parser.add_data_file(fake_data_fn.format(v))
    assert parser.pop_data_file() == fake_data_fn.format('i')
    assert parser.pop_data_file() == fake_data_fn.format('j')
    assert parser.pop_data_file() == fake_data_fn.format('k')

def test_remove_data_file(parser):
    fake_data_fn = './rawdata/no_such_data_{}.csv'
    parser.add_data_file(fake_data_fn.format('i'))
    # data removal normal operation
    parser.remove_data_file(fake_data_fn.format('i'))
    assert fake_data_fn.format('i') not in parser._file_queue
    # remove data file that doesn't exist
    # TODO: make sure logging messages are captured
    parser.remove_data_file(fake_data_fn.format('i'))

def test_open_data_file(parser):
    # TODO: make sure logging messages are captured
    assert parser._data_handle is None
    parser._open_data_file('./tests/__init__.py')
    assert isinstance(parser._data_handle, file)

def test_close_data_file(parser):
    # Make sure the function still works even when no data files have been opened
    parser._close_data_file()
    parser._open_data_file('./tests/__init__.py')
    # file closing normal operation
    parser._close_data_file()
    assert not isinstance(parser._data_handle, file)
