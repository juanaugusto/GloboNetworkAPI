# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolTestDeleteV3Case(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_delete_success(self):
        """ Test if delete pool passing id of existent pool returns success """
        response = self.client.delete(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % (response.status_code))

    def test_delete_error(self, expected_status_code=400):
        """ Test if delete pool passing id of inexistent pool returns error """
        response = self.client.delete(
            '/api/v3/pool/999999/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(expected_status_code, response.status_code, "Status code should be %s and was %s" % (expected_status_code, response.status_code))

    # test will not be executed by jenkins
    def wtest_delete_deployed_pool(self, name_file='api_pools/tests/json/delete/deployed_pool.json', expected_insert_code=201):
        # delete
        self.client.delete(
            '/api/v3/pool/1/',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(expected_insert_code, response.status_code,
                         "Status code should be %s and was %s" % (expected_insert_code, response.status_code))

        # deploy
        response = self.client.post(
            '/api/v3/pool/deploy/' + str(response.data[0]['id']) + '/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(expected_insert_code, response.status_code,
                         "Status code should be %s and was %s" % (expected_insert_code, response.status_code))

        # delete deployed pool
        self.client.delete(
            '/api/v3/pool/1/',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
