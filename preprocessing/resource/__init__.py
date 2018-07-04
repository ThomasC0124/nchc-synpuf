import os
import json

SCRIPT_DIR = os.path.dirname(__file__)

def _load_header(fn_in):
    with open(fn_in, 'r') as fp_in:
        header = json.load(fp_in)
    return header

beneficiary_summary_header = _load_header(os.path.join(SCRIPT_DIR, 'beneficiarySummaryHeader.json'))
inpatient_claim_header = _load_header(os.path.join(SCRIPT_DIR, 'inpatientClaimHeader.json'))
outpatient_claim_header = _load_header(os.path.join(SCRIPT_DIR, 'outpatientClaimHeader.json'))
carrier_claim_header = _load_header(os.path.join(SCRIPT_DIR, 'carrierClaimHeader.json'))
pde_header = _load_header(os.path.join(SCRIPT_DIR, 'prescriptionDrugEventHeader.json'))
