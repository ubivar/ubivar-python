import datetime
import unittest2
import urlparse

from mock import Mock, ANY

import oriskami

from oriskami.test.helper import (OriskamiAPIRequestorTestCase)

VALID_API_METHODS = ('get', 'post', 'delete')


class GMT1(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=1)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "Europe/Prague"


class APIHeaderMatcher(object):
    EXP_KEYS = [
        'Authorization',
        'Oriskami-Version',
        'User-Agent',
        'X-Oriskami-Client-User-Agent',
    ]
    METHOD_EXTRA_KEYS = {"post": ["Content-Type"]}

    def __init__(self, api_key=None, extra={}, request_method=None,
                 user_agent=None, app_info=None):
        self.request_method = request_method
        self.api_key = api_key or oriskami.api_key
        self.extra = extra
        self.user_agent = user_agent
        self.app_info = app_info

    def __eq__(self, other):
        return (self._keys_match(other) and
                self._auth_match(other) and
                self._user_agent_match(other) and
                self._x_oriskami_ua_contains_app_info(other) and
                self._extra_match(other))

    def _keys_match(self, other):
        expected_keys = list(set(self.EXP_KEYS + self.extra.keys()))
        if self.request_method is not None and self.request_method in \
                self.METHOD_EXTRA_KEYS:
            expected_keys.extend(self.METHOD_EXTRA_KEYS[self.request_method])
        return (sorted(other.keys()) == sorted(expected_keys))

    def _auth_match(self, other):
        return other['Authorization'] == "Bearer %s" % (self.api_key,)

    def _user_agent_match(self, other):
        if self.user_agent is not None:
            return other['User-Agent'] == self.user_agent

        return True

    def _x_oriskami_ua_contains_app_info(self, other):
        if self.app_info:
            ua = oriskami.util.json.loads(other['X-Oriskami-Client-User-Agent'])
            if 'application' not in ua:
                return False
            return ua['application'] == self.app_info

        return True

    def _extra_match(self, other):
        for k, v in self.extra.iteritems():
            if other[k] != v:
                return False

        return True


class QueryMatcher(object):

    def __init__(self, expected):
        self.expected = sorted(expected)

    def __eq__(self, other):
        query = urlparse.urlsplit(other).query or other

        parsed = oriskami.util.parse_qsl(query)
        return self.expected == sorted(parsed)


class UrlMatcher(object):

    def __init__(self, expected):
        self.exp_parts = urlparse.urlsplit(expected)

    def __eq__(self, other):
        other_parts = urlparse.urlsplit(other)

        for part in ('scheme', 'netloc', 'path', 'fragment'):
            expected = getattr(self.exp_parts, part)
            actual = getattr(other_parts, part)
            if expected != actual:
                print 'Expected %s "%s" but got "%s"' % (
                    part, expected, actual)
                return False

        q_matcher = QueryMatcher(oriskami.util.parse_qsl(self.exp_parts.query))
        return q_matcher == other


class APIRequestorRequestTests(OriskamiAPIRequestorTestCase):
    ENCODE_INPUTS = {
        'dict': {
            'astring': 'bar',
            'anint': 5,
            'anull': None,
            'adatetime': datetime.datetime(2013, 1, 1, tzinfo=GMT1()),
            'atuple': (1, 2),
            'adict': {'foo': 'bar', 'boz': 5},
            'alist': ['foo', 'bar'],
        },
        'list': [1, 'foo', 'baz'],
        'string': 'boo',
        'unicode': u'\u1234',
        'datetime': datetime.datetime(2013, 1, 1, second=1, tzinfo=GMT1()),
        'none': None,
    }

    ENCODE_EXPECTATIONS = {
        'dict': [
            ('%s[astring]', 'bar'),
            ('%s[anint]', 5),
            ('%s[adatetime]', 1356994800),
            ('%s[adict][foo]', 'bar'),
            ('%s[adict][boz]', 5),
            ('%s[alist][]', 'foo'),
            ('%s[alist][]', 'bar'),
            ('%s[atuple][]', 1),
            ('%s[atuple][]', 2),
        ],
        'list': [
            ('%s[]', 1),
            ('%s[]', 'foo'),
            ('%s[]', 'baz'),
        ],
        'string': [('%s', 'boo')],
        'unicode': [('%s', oriskami.util.utf8(u'\u1234'))],
        'datetime': [('%s', 1356994801)],
        'none': [],
    }

    def check_call(self, meth, abs_url=None, headers=None,
                   post_data=None, requestor=None):
        if not abs_url:
            abs_url = 'https://api.oriskami.com%s' % (self.valid_path,)
        if not requestor:
            requestor = self.requestor
        if not headers:
            headers = APIHeaderMatcher(request_method=meth)

        self.http_client.request.assert_called_with(
            meth, abs_url, headers, post_data)

    @property
    def valid_path(self):
        return '/foo'

    def encoder_check(self, key):
        stk_key = "my%s" % (key,)

        value = self.ENCODE_INPUTS[key]
        expectation = [(k % (stk_key,), v) for k, v in
                       self.ENCODE_EXPECTATIONS[key]]

        stk = []
        fn = getattr(oriskami.api_requestor.APIRequestor, "encode_%s" % (key,))
        fn(stk, stk_key, value)

        if isinstance(value, dict):
            expectation.sort()
            stk.sort()

        self.assertEqual(expectation, stk)

    def _test_encode_naive_datetime(self):
        stk = []

        oriskami.api_requestor.APIRequestor.encode_datetime(
            stk, 'test', datetime.datetime(2013, 1, 1))

        # Naive datetimes will encode differently depending on your system
        # local time.  Since we don't know the local time of your system,
        # we just check that naive encodings are within 24 hours of correct.
        self.assertTrue(60 * 60 * 24 > abs(stk[0][1] - 1356994800))

    def test_dictionary_list_encoding(self):
        params = {
            'foo': {
                '0': {
                    'bar': 'bat',
                }
            }
        }
        encoded = list(oriskami.api_requestor._api_encode(params))
        key, value = encoded[0]

        self.assertEqual('foo[0][bar]', key)
        self.assertEqual('bat', value)

    def test_fails_without_api_key(self):
        oriskami.api_key = None

        self.assertRaises(oriskami.error.AuthenticationError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_not_found(self):
        self.mock_response('{"error": {}}', 404)

        self.assertRaises(oriskami.error.InvalidRequestError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_authentication_error(self):
        self.mock_response('{"error": {}}', 401)

        self.assertRaises(oriskami.error.AuthenticationError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_permissions_error(self):
        self.mock_response('{"error": {}}', 403)

        self.assertRaises(oriskami.error.PermissionError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_rate_limit_error(self):
        self.mock_response('{"error": {}}', 429)

        self.assertRaises(oriskami.error.RateLimitError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_server_error(self):
        self.mock_response('{"error": {}}', 500)

        self.assertRaises(oriskami.error.APIError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_invalid_json(self):
        self.mock_response('{', 200)

        self.assertRaises(oriskami.error.APIError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_invalid_method(self):
        self.assertRaises(oriskami.error.APIConnectionError,
                          self.requestor.request,
                          'foo', 'bar')


if __name__ == '__main__':
    unittest2.main()
