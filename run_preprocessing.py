import sys
import json
import logging
import argparse

from preprocessing import BeneficiarySummaryParser
from preprocessing import ClaimParser
from util import (
    configure_logger,
    load_json
)

def main(args):
    logger = logging.getLogger(__name__)
    configure_logger(logger, args.log_fn)
    config = load_json(args.config)

    beneficiary_summary = run_beneficiary_summary_parser(args.sample_num, config, logger)
    claim_summary = {}
    for claim_type in ['inpatient', 'outpatient', 'carrier', 'pde']:
        claims = run_claim_parser(claim_type, args.sample_num, config[claim_type], logger)
        claim_summary[claim_type] = claims

    combine_files(
        beneficiary_summary, claim_summary, config['output'].replace('*', args.sample_num), logger
    )

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

def combine_files(beneficiary, claims, output_fn, logger):
    with open(output_fn, 'wb') as fp:
        for i, member_id in enumerate(beneficiary.keys()):
            member_doc = beneficiary.pop(member_id)
            # medical claims
            member_inp_claims = claims['inpatient'].pop(member_id, [])
            member_outp_claims = claims['outpatient'].pop(member_id, [])
            member_car_claims = claims['carrier'].pop(member_id, [])
            member_claims = sorted(
                member_inp_claims+member_outp_claims+member_car_claims,
                key=lambda claim: claim['startDate']
            )
            if len(member_claims) > 0:
                member_doc['medClaims'] = member_claims
            # prescription fills
            member_fills = claims['pde'].pop(member_id, [])
            if len(member_fills) > 0:
                member_doc['rxFills'] = member_fills

            member_doc['memberID'] = member_id
            fp.write(json.dumps(member_doc)+'\n')
            if (i+1) % 1000 == 0:
                logger.info('{} member docs processed'.format(i+1))

    logger.info('{} member docs processed'.format(i+1))

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='DE-SynPUF processing program')
    argparser.add_argument('sample_num', help='data sample number')
    argparser.add_argument('config', help='full path to the config file')
    argparser.add_argument('log_fn', help='full path to the log file')

    args = argparser.parse_args()
    main(args)
