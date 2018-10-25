import logging

from datetime import datetime
from collections import Counter

class Builder(object):
    def __init__(self):
        self.logger = logging.getLogger('Builder')
        self._common_dx_set = set()
        self._common_proc_set = set()

    def __repr__(self):
        desc = '<Matrix builder>'
        return desc

    def find_common_codes(self, json_data, num_dx_common, num_proc_common):
        dx_counter = Counter()
        proc_counter = Counter()
        for member_id, member_doc in json_data.iteritems():
            for claim in member_doc['medClaims']:
                dx_counter.update(claim['diagnoses'])
                proc_counter.update(claim['procedures'])
        for dx, count in dx_counter.most_common(num_dx_common):
            self._common_dx_set.add(dx)
        if len(dx_counter) < num_dx_common:
            self.logger.info(
                'only found {} common Dx codes, less than the expected {}'.format(len(dx_counter),
                                                                                  num_dx_common)
            )
        for proc, count in proc_counter.most_common(num_proc_common):
            self._common_proc_set.add(proc)
        if len(proc_counter) < num_proc_common:
            self.logger.info(
                'only found {} common Proc codes, less than the expected {}'.format(len(proc_counter),
                                                                                    num_proc_common)
            )

    def build_matrix(self, json_data, mode=None):
        header = []
        matrix = []
        if len(self._common_dx_set) == 0 or len(self._common_proc_set) == 0:
            self.logger.warning(
                'please run {}.find_common_codes(...) first to get the most common codes'.format(
                    self.__class__.__name__
                )
            )
            return header, matrix

        header.extend([
            'age', 'gender', 'race', 'ESRDStatus', 'Alzheimer', 'CHF', 'CKD', 'cancer', 'COPD',
            'depression', 'diabetes', 'ischemicHD', 'osteoporosis', 'RAOA', 'stroke'
        ])
        header.extend(list(self._common_dx_set)+list(self._common_proc_set))
        for member_id, member_doc in json_data.iteritems():
            member_demographic = self._extract_demographics(
                member_doc, datetime.strptime(
                    member_doc['medClaims'][member_doc['tkrClaimIdx']]['startDate'], '%Y%m%d'
                )
            )
            # TODO: add "mode" to "build_matrix" so that "_extract_medical" extract different
            # ranges of claims
            member_medical = self._extract_medical(
                member_doc, starting_idx=0, ending_idx=member_doc['tkrClaimIdx']
            )
            member_demographic.update(member_medical)
            member_list = self._convert_container_to_list(member_demographic, header)
            matrix.append(member_list)
        return header, matrix

    def _extract_demographics(self, member_doc, reference_date):
        age = (reference_date-datetime.strptime(member_doc['DOB'], '%Y%m%d')).days/365.25
        gender = (member_doc['gender'] == 'female')
        demographic = {
            'age': age,
            'gender': member_doc['gender'],
            'race': member_doc['race']
        }
        # cc stands for chronic condition
        for cc in [
            'ESRDStatus', 'Alzheimer', 'CHF', 'CKD', 'cancer', 'COPD', 'depression', 'diabetes',
            'ischemicHD', 'osteoporosis', 'RAOA', 'stroke'
        ]:
            has_status = max(member_doc.get(cc, {'cc': 0}).values())==1
            demographic[cc] = has_status
        return demographic

    def _extract_medical(self, member_doc, starting_idx, ending_idx):
        medical = {}
        dx_counter = Counter()
        proc_counter = Counter()
        for i, claim in enumerate(member_doc['medClaims']):
            if i < starting_idx or i > ending_idx:
                break
            dx_counter.update(claim.get('diagnoses', []))
            proc_counter.update(claim.get('procedures', []))
        for code, count in dx_counter.iteritems():
            if code in self._common_dx_set:
                medical[code] = count
        for code, count in proc_counter.iteritems():
            if code in self._common_proc_set:
                medical[code] = count
        return medical

    def _convert_container_to_list(self, container, header):
        """Convert dictionary `container` to a list for CSV reports with required fields specified
            in `header`
        """
        list_to_output = []
        for field in header:
            list_to_output.append(container.get(field, 0))
        return list_to_output
