import re

import requests
import json
from requests.adapters import HTTPAdapter, Retry
class Uniprot:
    def __init__(self):
        pass

    def search(self):
        pass

    def get_next_link(self, headers):
        re_next_link = re.compile(r'<(.+)>; rel="next"')
        if "Link" in headers:
            match = re_next_link.match(headers["Link"])
            if match:
                return match.group(1)

    def get_batch(self, batch_url):
        while batch_url:
            response = self.session.get(batch_url)
            response.raise_for_status()
            total = response.headers["x-total-results"]
            yield response, total
            batch_url = self.get_next_link(response.headers)


    def search_by_accession(self, accession: str):

        retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        url = f'https://rest.uniprot.org/uniprotkb/search?query={accession}%20AND%20(reviewed:true)'
        results = []
        for batch, total in self.get_batch(url):
            data = json.loads(batch.text)
            results += data['results']
        return results


if __name__ == "__main__":
    uniprot = Uniprot()
    results = uniprot.search_by_accession("yor317w")
    is_transporter = False
    for cross_ref in results[0]['uniProtKBCrossReferences']:
        if cross_ref['database'] == 'GO':
            for prop in  cross_ref['properties']:
                print(prop['value'])
    # for keyword in results[0]['keywords']:
    #     if 'category' in keyword.keys() and keyword['category'] == 'Biological process':
    #         if "transport"  in keyword['name'].lower():
    #             is_transporter = True
    # print(is_transporter)