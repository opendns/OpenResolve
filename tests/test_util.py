from tests import BaseTest

from mock import patch
import dns

from resolverapi.util.dns_query import parse_query


TEST_DOMAIN = 'testdomain.com.'


def make_answer(rdtype, answers=None, additionals=None, authorities=None):
    """For mocking an answer. We make an answer without any message (what would
    normally come over the network, to be parsed. We instead make a blank
    object for the sake of test complexity, and later attach the appropriate\
    rrsets to the answer.

    This may cause some tests to fail that test attributes that are assigned
    during the creation of an Answer (flags?).

    The answers, additionals, and authorities should be lists of strings, with
    data fields space-separated. Each string representing one RR. See RFC for
    order of field per type.
    ex: MX would be '<Preference> <Mail Exchanger>'
    """
    answer = dns.resolver.Answer(
        dns.name.from_text(TEST_DOMAIN),
        getattr(dns.rdatatype, rdtype.upper()),
        dns.rdataclass.IN,
        dns.message.from_text(''),
        raise_on_no_answer=False
    )
    if answers:
        rrset = dns.rrset.from_text(TEST_DOMAIN, 60, 'IN', rdtype, *answers)
        answer.response.answer = [rrset]
    if additionals:
        rrset = dns.rrset.from_text(TEST_DOMAIN, 60, 'IN', rdtype, *additionals)
        answer.response.answer = [rrset]
    if authorities:
        rrset = dns.rrset.from_text(TEST_DOMAIN, 60, 'IN', rdtype, *authorities)
        answer.response.authority = [rrset]
    return answer


@patch('resolverapi.endpoints.dns_resolver.query')
class ParseQueryTests(BaseTest):

    def setUp(self):
        super(ParseQueryTests, self).setUp()

    def lookup(self, rdtype):
        return super(ParseQueryTests, self).get(
            '%s/%s' % (rdtype, TEST_DOMAIN))

    def test_a_lookup(self, query, rdtype='A'):
        rrs = ['10.0.0.1', '10.0.0.2']
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': TEST_DOMAIN
            },
            'AnswerSection': [
                {'Name': TEST_DOMAIN, 'TTL': 60, 'Type': rdtype,
                 'Class': 'IN', 'Address': '10.0.0.1'},
                {'Name': TEST_DOMAIN, 'TTL': 60, 'Type': rdtype,
                 'Class': 'IN', 'Address': '10.0.0.2'}
            ]
        }, resp)

    def test_aaaa_lookup(self, query, rdtype='AAAA'):
        rrs = ['2607:f8b0:4005:802::1008']
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': TEST_DOMAIN
            },
            'AnswerSection': [
                {'Name': TEST_DOMAIN, 'TTL': 60, 'Type': rdtype,
                 'Class': 'IN', 'Address': '2607:f8b0:4005:802::1008'}
            ]
        }, resp)

    def test_mx_lookup(self, query, rdtype='MX'):
        rrs = ['10 mx1.%s' % TEST_DOMAIN, '20 mx2.%s' % TEST_DOMAIN]
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': TEST_DOMAIN
            },
            'AnswerSection': [
                {'Name': TEST_DOMAIN, 'Preference': 10,
                 'MailExchanger': 'mx1.%s' % TEST_DOMAIN, 'TTL': 60,
                 'Type': rdtype, 'Class': 'IN'},
                {'Name': TEST_DOMAIN, 'Preference': 20,
                 'MailExchanger': 'mx2.%s' % TEST_DOMAIN, 'TTL': 60,
                 'Type': rdtype, 'Class': 'IN'},
            ]
        }, resp)

    def test_ns_lookup(self, query, rdtype='NS'):
        rrs = ['ns1.%s' % TEST_DOMAIN, 'ns2.%s' % TEST_DOMAIN]
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': 'testdomain.com.'},
            'AnswerSection': [
                {'Target': 'ns1.testdomain.com.', 'Class': 'IN',
                 'Name': TEST_DOMAIN, 'TTL': 60, 'Type': rdtype},
                {'Target': 'ns2.testdomain.com.', 'Class': 'IN',
                 'Name': TEST_DOMAIN, 'TTL': 60, 'Type': rdtype}
            ]
        }, resp)

    def test_cname_lookup(self, query, rdtype='SOA'):
        """The QuestionSection's Qtype ends up being SOA, even though CNAME was
        the query. See:
        github.com/rthalley/dnspython/blob/43c14fd73b3b
          94211ff8bfad8f894b48cce4e577/dns/resolver.py#L95
        """
        rrs = ['auth1.{0} hostmaster.{0} '
               '1412191487 16384 2048 1048576 2560'.format(TEST_DOMAIN)]
        query.return_value = make_answer(rdtype, authorities=rrs)

        resp, code = self.lookup('CNAME')
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': 'testdomain.com.'},
            'AnswerSection': [],
            'AuthoritySection': [
                {'MasterServerName': 'auth1.%s' % TEST_DOMAIN,
                 'MaintainerName': 'hostmaster.%s' % TEST_DOMAIN,
                 'Serial': 1412191487,
                 'Refresh': 16384,
                 'Retry': 2048,
                 'Expire': 1048576,
                 'NegativeTtl': 2560,
                 'Class': 'IN', 'Type': rdtype, 'TTL': 60, 'Name': TEST_DOMAIN}
            ]
        }, resp)

    def test_txt_lookup(self, query, rdtype='TXT'):
        rrs = ['"here\'s a bunch of text"', '"guess what? here\'s more"']
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': 'testdomain.com.'},
            'AnswerSection': [
                {'TxtData': '"here\'s a bunch of text"', 'TTL': 60,
                 'Type': rdtype, 'Class': 'IN', 'Name': 'testdomain.com.'},
                {'TxtData': '"guess what? here\'s more"', 'TTL': 60,
                 'Type': rdtype, 'Class': 'IN', 'Name': 'testdomain.com.'}
            ],
        }, resp)

    def test_ptr_lookup(self, query, rdtype="PTR"):
        rrs = ['target.domain.com.']
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': 'testdomain.com.'},
            'AnswerSection': [
                {'Target': 'target.domain.com.', 'TTL': 60, 'Type': rdtype,
                 'Class': 'IN', 'Name': TEST_DOMAIN}
            ],
        }, resp)

    def test_naptr_lookup(self, query, rdtype="NAPTR"):
        # ex: dig naptr 4.4.2.2.3.3.5.6.8.1.4.4.e164.arpa
        rrs = ['100 20 "u" "E2U+pstn:tel" "!^(.*)$!tel:\\\\1!" .']
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': 'testdomain.com.'},
            'AnswerSection': [
                {'Flags': 'u',
                 'Order': 100,
                 'Preference': 20,
                 'Regexp': '!^(.*)$!tel:\\1!',
                 'Replacement': '.',
                 'Service': 'E2U+pstn:tel',
                 'Class': 'IN', 'Type': rdtype, 'TTL': 60, 'Name': TEST_DOMAIN}
            ],
        }, resp)

    def test_loc_lookup(self, query, rdtype="LOC"):
        # ex: dig loc statdns.net
        rrs = ['52 22 23.000 N 4 53 32.000 E -2.00m']
        query.return_value = make_answer(rdtype, answers=rrs)

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'QuestionSection': {
                'Qclass': 'IN', 'Qtype': rdtype, 'Qname': 'testdomain.com.'},
            'AnswerSection': [
                {'Longitude': [4, 53, 32, 0], 'Latitude': [52, 22, 23, 0],
                 'Altitude': -2.0, 'Class': 'IN', 'Type': rdtype, 'TTL': 60,
                 'Name': TEST_DOMAIN}
            ],
        }, resp)

    @patch('resolverapi.endpoints.parse_query')
    def test_query_section(self, parse_query_mock, query, rdtype='A'):
        query.return_value = make_answer(rdtype)

        def mod_parse_query(answer, *args, **kwargs):
            # replace the nameserver and duration
            return parse_query(answer, '1.1.1.1', 1)
        parse_query_mock.side_effect = mod_parse_query

        resp, code = self.lookup(rdtype)
        self.assert200(code)
        self.assertDictContainsSubset({
            'Query': {
                'Server': '1.1.1.1',
                'Duration': 1
            }
        }, resp)
