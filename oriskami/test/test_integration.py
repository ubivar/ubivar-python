# -*- coding: utf-8 -*-
import os
import sys
import unittest2
import oriskami

from mock import patch
from oriskami.test.helper import (OriskamiTestCase, NOW)


class FunctionalTests(OriskamiTestCase):
    request_client = oriskami.http_client.Urllib2Client

    def setUp(self):
        super(FunctionalTests, self).setUp()

        def get_http_client(*args, **kwargs):
            return self.request_client(*args, **kwargs)

        self.client_patcher = patch(
            'oriskami.http_client.new_default_http_client')

        client_mock = self.client_patcher.start()
        client_mock.side_effect = get_http_client

    def tearDown(self):
        super(FunctionalTests, self).tearDown()

        self.client_patcher.stop()


class RequestsFunctionalTests(FunctionalTests):
    request_client = oriskami.http_client.RequestsClient


if __name__ == '__main__':
    unittest2.main()
