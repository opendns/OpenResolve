# -*- coding: utf-8 -*-

from tests import BaseTest

from mock import patch
from dns.resolver import NXDOMAIN, NoNameservers
from dns.exception import Timeout

from tests.test_util import make_answer


class LookupRecordTests(BaseTest):

    def setUp(self):
        super(LookupRecordTests, self).setUp()

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_no_nameservers(self, query):
        def raises_no_nameservers(*args, **kwargs):
            raise NoNameservers
        query.side_effect = raises_no_nameservers

        domain = 'nonameserversatthisdomain.tld'
        resp, code = self.get('NS/%s' % domain)
        self.assert404(code)
        self.assertDictEqual(resp, {
            'message': 'No nameservers for %s' % domain})

    def test_invalid_type(self):
        resp, code = self.get('NA/google.com')
        self.assert400(code)
        self.assertDictEqual(resp, {'message': 'NA type is not supported'})

    def test_invalid_domain(self):
        domain = 'invalid&domain'
        resp, code = self.get('NS/%s' % domain)
        self.assert400(code)
        self.assertDictEqual(resp, {
            'message': '%s is not a valid domain name' % domain})

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_timeout(self, query):
        resolvers = ['1.1.1.1', '2.2.2.2']
        self.app.config['RESOLVERS'] = resolvers
        def raises_timeout(*args, **kwargs):
            raise Timeout
        query.side_effect = raises_timeout

        domain = 'doesnotmatter.wat'
        resp, code = self.get('A/%s' % domain)
        self.assert503(code)
        self.assertDictEqual(resp, {
            'message': 'All nameservers timed out.'})
        self.assertEquals(query.call_count, len(resolvers))

    def test_root_200(self):
        resp, code = self.get('')
        self.assert200(code)

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_idn_domain(self, query):
        query.return_value = make_answer('A', answers=['1.1.1.1'])

        domain = u'ąćęłńóśźż.pl'
        resp, code = self.get('a/%s' % domain)
        self.assert200(code)

    def test_invalid_idn_domain(self):
        domain = u'ąćęłń óśźż.pl'
        resp, code = self.get('a/%s' % domain)
        self.assert400(code)
        self.assertDictEqual(resp, {
            'message': '%s is not a valid domain name' % domain})

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_nonexistent_idn_domain(self, query):
        def raises_no_nameservers(*args, **kwargs):
            raise NoNameservers
        query.side_effect = raises_no_nameservers

        domain = u'ąćęłńóśźż.plllll'
        resp, code = self.get('a/%s' % domain)
        self.assert404(code)
        self.assertDictEqual(resp, {
            'message': "No nameservers for %s" % domain})


class ReverseLookupTests(BaseTest):

    def setUp(self):
        super(ReverseLookupTests, self).setUp()
        self.path = 'reverse/%s'

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_ipv4(self, query):
        query.return_value = make_answer('PTR', answers=['target.domain.com.'])

        ipv4_addr = '208.67.222.222'
        resp, code = self.get(self.path % ipv4_addr)
        self.assert200(code)

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_ipv6(self, query):
        query.return_value = make_answer('PTR', answers=['target.domain.com.'])

        ipv6_addr = '2001:4860:4860::8888'
        resp, code = self.get(self.path % ipv6_addr)
        self.assert200(code)

    def test_invalid_addr(self):
        ipv4_addr = '208.67.222.222.999'
        resp, code = self.get(self.path % ipv4_addr)
        self.assert400(code)

        ipv4_addr = 'junk'
        resp, code = self.get(self.path % ipv4_addr)
        self.assert400(code)

        ipv4_addr = '256.1.1.1'
        resp, code = self.get(self.path % ipv4_addr)
        self.assert400(code)

    @patch('resolverapi.endpoints.dns_resolver.query')
    def test_nxdomain(self, query):
        def raises_nxdomain(*args, **kwargs):
            raise NXDOMAIN
        query.side_effect = raises_nxdomain

        ipv4_addr = '1.1.1.1'
        resp, code = self.get(self.path % ipv4_addr)
        self.assert404(code)
