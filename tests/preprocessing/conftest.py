import pytest

@pytest.fixture(scope='module')
def fake_beneficiary_summary_data_fn():
    return './random_folder/fake_beneficiary_summary.csv'

@pytest.fixture(scope='module')
def sample_beneficiary_summary_data_fns():
    fns = [
        './rawdata/Sample_Beneficiary_Summary_File_2008.csv',
        './rawdata/Sample_Beneficiary_Summary_File_2009.csv',
        './rawdata/Sample_Beneficiary_Summary_File_2010.csv'
    ]
    return fns

@pytest.fixture(scope='module')
def sample_inpatient_claim_data_fn():
    return './rawdata/Sample_Inpatient_Claims.csv'

@pytest.fixture(scope='module')
def sample_outpatient_claim_data_fn():
    return './rawdata/Sample_Outpatient_Claims.csv'

