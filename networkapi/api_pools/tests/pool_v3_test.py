# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)

# Overriding the standard Python dict sort


class PoolTestV3Case(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_valid_post_after_equals_valid_put(self):
        """ test_valid_post_after_equals_valid_put"""

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put_and_post.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put_and_post.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code, "Status code should be 500 and was %s" % response.status_code)
