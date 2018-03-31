from urllib.parse import urljoin

import requests
from requests.structures import CaseInsensitiveDict as cidict


class TempoClient(object):
    def __init__(self, token, base_url='https://api.tempo.io/2/'):
        self.token = token
        self.base_url = base_url

    def _request(self, resource, method='GET', **kwargs):
        headers = kwargs.setdefault('headers', cidict())
        headers.setdefault('Authorization', 'Bearer {}'.format(self.token))
        url = urljoin(self.base_url, resource.lstrip('/'))

        resp = requests.request(method, url, **kwargs)
        resp.raise_for_status()

        return resp.json()

    def accounts(self):
        return self._request('accounts')

    def worklogs(self, from_date=None, to_date=None):
        results = []
        offset = 0

        while True:
            query = {
                'offset': offset,
                'limit': 1000,
            }
            if from_date and to_date:
                query['from'] = '{:%Y-%m-%d}'.format(from_date)
                query['to'] = '{:%Y-%m-%d}'.format(to_date)

            response = self._request('worklogs', params=query)
            assert (response['metadata']['offset'] == offset)
            offset = response['metadata']['offset'] + response['metadata']['count']

            results.extend(response['results'])

            if not response['metadata'].get('next'):
                break

        return results
