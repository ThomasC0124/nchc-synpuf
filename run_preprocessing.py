import sys
import json
import logging
import argparse

from preprocessing import BeneficiarySummaryParser
from preprocessing import ClaimParser
from util import (
    configure_logger,
    save_to_json
)

def main(args):
    logger = logging.getLogger(__name__)
    configure_logger(logger, args.log_fn)
    with open(args.config, 'r') as fp:
        config = json.load(fp)

    sample_beneficiary_summary = run_beneficiary_summary_parser(args.sample_num, config, logger)
    sample_claims = {}
    for claim_type in ['inpatient', 'outpatient', 'carrier', 'pde']:
        claims = run_claim_parser(claim_type, args.sample_num, config[claim_type], logger)
        sample_claims[claim_type] = claims

    combine_files(sample_beneficiary_summary, sample_claims['inpatient'], sample_claims['outpatient'],
                  sample_claims['carrier'], sample_claims['pde'])

    save_to_json(sample_beneficiary_summary, config['output'].replace('*', args.sample_num))

def run_beneficiary_summary_parser(sample_num, config, logger):
    """Run beneficiary summary parser"""
    logger.info('Start parsing beneficiary summary sample "{}"...'.format(sample_num))
    parser = BeneficiarySummaryParser()
    for raw_data_fn in config['beneficiary']:
        raw_data_fn = raw_data_fn.replace('*', sample_num)
        logger.info('Adding {} to the queue...'.format(raw_data_fn))
        parser.add_data_file(raw_data_fn)

    logger.info('Parsing beneficiary summary files...')
    output_data_fns = parser.parse_data()

    logger.info('Combining parsed beneficiary summary files...')
    bene = parser.combine_data(
        {
            year: parsed_data_fn for year, parsed_data_fn in zip(
                ['2008', '2009', '2010'], output_data_fns
            )
        }
    )
    logger.info(
        'Finish parsing - {} beneficiaries found in the beneficiary summary sample "{}"'.format(
            len(bene), sample_num
        )
    )
    return bene

def run_claim_parser(claim_type, sample_num, raw_data_fns, logger):
    """Run `claim_type` claim parser"""
    logger.info('Start parsing {} claim sample "{}"...'.format(claim_type, sample_num))
    parser = ClaimParser(claim_type)
    for raw_data_fn in raw_data_fns:
        raw_data_fn = raw_data_fn.replace('*', sample_num)
        logger.info('Adding {} to the queue...'.format(raw_data_fn))
        parser.add_data_file(raw_data_fn)

    logger.info('Parsing {} claim files...'.format(claim_type))
    output_data_fns = parser.parse_data()

    logger.info('Merging parsed {} claim files...'.format(claim_type))
    for fn in output_data_fns:
        parser.add_data_file(fn)
    claims = parser.merge_claim_lines()

    logger.info(
        'Finish parsing - {} beneficiaries found in the {} claims sample "{}"'.format(
            len(claims), claim_type, sample_num
        )
    )
    return claims

def combine_files(bene, inp_claims, outp_claims, car_claims, pde_claims):
    for member_id in bene:
        member_doc = bene[member_id]
        member_inp_claims = inp_claims.get(member_id, [])
        member_outp_claims = outp_claims.get(member_id, [])
        member_car_claims = car_claims.get(member_id, [])
        member_doc['medClaims'] = sorted(
            member_inp_claims+member_outp_claims+member_car_claims,
            key=lambda claim: claim['startDate']
        )
        member_pde_claims = pde_claims.get(member_id, [])
        member_doc['rxFills'] = member_pde_claims

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='DE-SynPUF processing program')
    argparser.add_argument('-l', '--log_fn',
                           help='full path to the log file', required=True)
    argparser.add_argument('-cfg', '--config',
                           help='full path to the config file', required=True)
    argparser.add_argument('-sn', '--sample_num',
                           help='data sample number', required=True)

    args = argparser.parse_args()
    main(args)
