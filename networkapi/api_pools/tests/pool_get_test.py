# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolTestGetV3Case(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success(self):
        """ Test if get of pool passing id of existent pool returns success """
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % (response.status_code))

    def test_get_error(self, expected_status_code=500):
        """ Test if get of pool passing id of inexistent pool returns error """
        response = self.client.get(
            '/api/v3/pool/999999/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(expected_status_code, response.status_code, "Status code should be %s and was %s" % (expected_status_code, response.status_code))
