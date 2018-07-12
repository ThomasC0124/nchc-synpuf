import pytest

from engineering.builder import Builder

def test_instantiation():
    builder = Builder()
    for method in ['load_data', 'add_mapper', 'build_matrix']:
        builder_method = getattr(builder, method, None)
        assert callable(builder_method)
