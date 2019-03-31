import pytest

@pytest.fixture
def fake_json_data():
    json_data = {
        'm111': {
            'DOB': '19900125',
            'gender': 'male',
            'race': 'asian',
            'tkrClaimIdx': 2,
            'medClaims': [
                {
                    'diagnoses': ['d1', 'd1', 'd2', 'd2'],
                    'procedures': ['p1', 'p1', 'p2', 'p3', 'p4'],
                    'startDate': '20080215',
                },
                {
                    'diagnoses': ['d2', 'd2', 'd3', 'd4'],
                    'procedures': ['p3', 'p4', 'p6'],
                    'startDate': '20080404',
                },
                {
                    'diagnoses': ['d5', 'd5', 'd6'],
                    'procedures': ['p1', 'p5'],
                    'startDate': '20080512',
                },
            ]
        },
        'm222': {
            'DOB': '19910401',
            'gender': 'female',
            'race': 'asian',
            'tkrClaimIdx': 2,
            'medClaims': [
                {
                    'diagnoses': ['d2', 'd3', 'd7', 'd8'],
                    'procedures': ['p1', 'p3', 'p4'],
                    'startDate': '20080131',
                },
                {
                    'diagnoses': ['d8'],
                    'procedures': ['p6', 'p8', 'p9'],
                    'startDate': '20080213',
                },
                {
                    'diagnoses': ['d1', 'd7', 'd8', 'd9'],
                    'procedures': ['p1', 'p5', 'p7', 'p8'],
                    'startDate': '20080501',
                },
                {
                    'diagnoses': ['d4', 'd5'],
                    'procedures': ['p1', 'p2', 'p8'],
                    'startDate': '20080630',
                },
            ]
        }
    }
    yield json_data
