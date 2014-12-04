import unittest
import json

from resolverapi import create_app


class BaseTest(unittest.TestCase):
    """ Ideas taken from
    github.com/nicolaiarocci/eve/blob/v0.4/eve/tests/__init__.py
    """

    def setUp(self):
        self.app = create_app('test')  # currently no test config

        self.test_client = self.app.test_client()

    def assert200(self, status):
        self.assertEqual(status, 200)

    def assert201(self, status):
        self.assertEqual(status, 201)

    def assert301(self, status):
        self.assertEqual(status, 301)

    def assert304(self, status):
        self.assertEqual(status, 304)

    def assert400(self, status):
        self.assertEqual(status, 400)

    def assert404(self, status):
        self.assertEqual(status, 404)

    def assert503(self, status):
        self.assertEqual(status, 503)

    def get(self, path, query='', headers=None):
        path = '/%s%s' % (path, query)
        if headers is None:
            headers = []  # example headers [('Origin', 'test.com')]
        r = self.test_client.get(path)
        return self.parse_response(r)

    def post(self, url, data, headers=None, content_type='application/json'):
        if headers is None:
            headers = []
        headers.append(('Content-Type', content_type))
        r = self.test_client.post(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def put(self, url, data, headers=None):
        if headers is None:
            headers = []
        headers.append(('Content-Type', 'application/json'))
        r = self.test_client.put(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def patch(self, url, data, headers=None):
        if headers is None:
            headers = []
        headers.append(('Content-Type', 'application/json'))
        r = self.test_client.patch(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def delete(self, url, headers=None):
        r = self.test_client.delete(url, headers=headers)
        return self.parse_response(r)

    def parse_response(self, r):
        try:
            v = json.loads(r.get_data())
        except ValueError:
            v = None
        return v, r.status_code
