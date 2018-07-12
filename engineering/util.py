from datetime import datetime

def whether_member_had_tkr(member_med_claims):
    """Check whether a member had TKR by searching for 
        DRG codes: 469, 470
        HCPCS/CPT procedure codes: 27447
        ICD-9 procedure codes: 8154, 8155

    Args:
        member_med_claims (list): member's medical claims

    Returns:
        had_tkr (bool): whether the member had TKR
        tkr_claim (dict|None): TKR claim when the member did have TKR; None otherwise
    """
    had_tkr = False
    tkr_claim = None
    for claim in member_med_claims:
        claim_drgs = claim.get('DRG', [])
        claim_cpt_procs = claim.get('procedures', [])
        claim_icd_procs = claim.get('procedureICDs', [])
        if (len(set(['469', '470']).intersection(claim_drgs)) > 0 or
            '27447' in claim_cpt_procs or
            len(set(['8154', '8155']).intersection(claim_icd_procs)) > 0):
            had_tkr = True
        if had_tkr:
            tkr_claim = claim.copy()
            break
    return had_tkr, tkr_claim

def whether_member_was_readmitted(member_med_claims, tkr_claim):
    """Check whether the member who had TKR was readmitted to a hospital within 90 days after TKR

    Args:
        member_med_claims (list): member's medical claims
        tkr_claim (dict): TKR claim when the member did have TKR; None otherwise

    Returns:
        was_readmitted (bool): whether the member was readmitted after TKR
        readmission_claim (dict|None): readmission claim when the member was readmitted;
            None otherwise
    """
    was_readmitted = False
    readmission_claim = None
    if tkr_claim is None:
        return was_readmitted, readmission_claim
    tkr_claim_date = datetime.strptime(
        tkr_claim.get('dischargeDate', tkr_claim['endDate']), '%Y%m%d'
    ).date()
    for claim in member_med_claims:
        # only inpatient claims since it's hospital admission
        if claim['claimType'] != 'inpatient':
            continue
        # only inpatient claims within 90 days after TKR
        claim_admission_date = datetime.strptime(claim['admissionDate'], '%Y%m%d').date()
        days_after_tkr = (claim_admission_date-tkr_claim_date).days
        if days_after_tkr < 0 or days_after_tkr > 90:
            continue
        # only inpatient claims with at least 1 day of admission
        claim_discharge_date = datetime.strptime(claim['dischargeDate'], '%Y%m%d').date()
        days_admission = (claim_discharge_date-claim_admission_date).days
        if days_admission < 1:
            continue
        for ins in claim['providerInstitution']:
            ins = int(ins)
            if (1 <= ins <= 839 or 1300 <= ins <= 1399):
                was_readmitted = True
                break
        if was_readmitted:
            readmission_claim = claim.copy()
            break
    return was_readmitted, readmission_claim
