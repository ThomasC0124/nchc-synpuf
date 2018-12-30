import csv
import argparse
import logging

from engineering import Builder
from engineering.util import (
    whether_member_had_tkr,
    whether_tkr_member_was_readmitted
)
from util import load_json

def main(args):
    members = load_json(args.json_fn_in)
    tkr_members = filter_out_tkr_members(members)
    label_readmitted_tkr_members(tkr_members)

    matrix_builder = Builder()
    matrix_builder.find_common_codes(tkr_members, args.num_dx, args.num_proc)
    header, matrix = matrix_builder.build_matrix(tkr_members, mode=None)

    with open(args.csv_fn_out, 'wb') as fp:
        writer = csv.writer(fp)
        writer.writerow(header)
        writer.writerows(matrix)

def filter_out_tkr_members(members):
    """Filter out TKR members"""
    tkr_members = {}
    for member_id, member_doc in members.iteritems():
        member_med_claims = member_doc.get('medClaims', [])
        had_tkr, tkr_claim_idx = whether_member_had_tkr(member_med_claims)
        if had_tkr:
            member_doc['tkrClaimIdx'] = tkr_claim_idx
            tkr_members[member_id] = member_doc
    return tkr_members

def label_readmitted_tkr_members(tkr_members):
    """Label TKR members by whether they were readmitted"""
    for member_id, member_doc in tkr_members.iteritems():
        member_med_claims = member_doc.get('medClaims', [])
        tkr_claim_idx = member_doc['tkrClaimIdx']
        tkr_claim = member_med_claims[tkr_claim_idx]
        was_readmitted, readmission_claim_idx = whether_tkr_member_was_readmitted(
            member_med_claims, tkr_claim
        )
        member_doc['was_readmitted'] = was_readmitted
        member_doc['readmissionClaimIdx'] = readmission_claim_idx

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='DE-SynPUF feature engineering program')
    argparser.add_argument('json_fn_in', help='full path to the Members_Full JSON file')
    argparser.add_argument('csv_fn_out', help='full path to the CSV file')
    argparser.add_argument('-dx', '--num_dx',
                           help='number of common Dx codes to look for', required=True)
    argparser.add_argument('-proc', '--num_proc',
                           help='number of common procedure codes to look for', required=True)

    args = argparser.parse_args()
    main(args)
