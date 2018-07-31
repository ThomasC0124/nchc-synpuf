import pytest

from datetime import datetime
from collections import Counter

from engineering.builder import Builder

def test_instantiation():
    builder = Builder()
    for method in ['find_common_codes', 'build_matrix']:
        builder_method = getattr(builder, method, None)
        assert callable(builder_method)

def test_find_common_codes(fake_json_data):
    num_dx_common = 4
    num_proc_common = 4
    builder = Builder()
    builder.find_common_codes(fake_json_data, num_dx_common, num_proc_common)
    all_claims = []
    for member_id, member_doc in fake_json_data.iteritems():
        for claim in member_doc['medClaims']:
            all_claims.append(claim)
    # check diagnoses
    assert len(builder._common_dx_set) <= num_dx_common
    common_code_set = _find_common_codes(all_claims, 'diagnoses', num_dx_common)
    assert builder._common_dx_set == common_code_set
    # check procedures
    assert len(builder._common_proc_set) <= num_proc_common
    common_code_set = _find_common_codes(all_claims, 'procedures', num_proc_common)
    assert builder._common_proc_set == common_code_set

def _find_common_codes(data, key, top_n_count):
    counter = Counter()
    for claim in data:
        counter.update(claim.get(key, []))
    common_code_set = set()
    for code, count in counter.most_common(top_n_count):
        common_code_set.add(code)
    return common_code_set

def test_extract_demographics(fake_json_data):
    builder = Builder()
    reference_date = datetime(2018, 7, 30)
    for member_id, member_doc in fake_json_data.iteritems():
        demographics = builder._extract_demographics(member_doc, reference_date)
        assert demographics['age'] == (
            reference_date-datetime.strptime(member_doc['DOB'], '%Y%m%d')
        ).days/365.25
        assert demographics['gender'] == member_doc['gender']
        assert demographics['race'] == member_doc['race']

def test_extract_medical(fake_json_data):
    num_dx_common = 3
    num_proc_common = 3
    builder = Builder()
    builder.find_common_codes(fake_json_data, num_dx_common, num_proc_common)

    for member_id, member_doc in fake_json_data.iteritems():
        dx_code_set = _find_common_codes(member_doc['medClaims'], 'diagnoses', None)
        proc_code_set = _find_common_codes(member_doc['medClaims'], 'procedures', None)

        medical = builder._extract_medical(member_doc, 0, len(member_doc['medClaims']))
        for code in medical:
            assert code in dx_code_set or code in proc_code_set

def test_build_matrix(fake_json_data):
    num_dx_common = 3
    num_proc_common = 3
    builder = Builder()
    builder.find_common_codes(fake_json_data, num_dx_common, num_proc_common)

    header, matrix = builder.build_matrix(fake_json_data)
    assert len(header) == 15+len(builder._common_dx_set)+len(builder._common_proc_set)
    assert len(matrix) == 2
