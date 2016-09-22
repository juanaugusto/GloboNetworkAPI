# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class VipRequestTestV3Case(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def wtest__post_valid_file_with_one_group_user_(self):
        self.execute_some_post_verify_success(
            'api_vip_request/tests/json/post/test_vip_request_post_valid_file_with_one_group_user.json')

    def wtest__post_valid_file_with_two_group_user_(self):
        self.execute_some_post_verify_success(
            'api_vip_request/tests/json/post/testvip_request_post_valid_file_with_two_group_user.json')

    def wtest__post_invalid_file_with_two_equal_group_user_(self):
        self.execute_some_post_verify_error(
            'api_vip_request/tests/json/post/test_vip_request_post_invalid_file_with_two_equal_group_user.json')

    def wtest__put_valid_file_with_one_group_user_(self):
        self.execute_some_put_verify_success(
            'api_vip_request/tests/json/put/test_vip_request_put_valid_file_with_one_group_user.json')

    def wtest__put_valid_file_with_two_group_user_(self):
        self.execute_some_put_verify_success(
            'api_vip_request/tests/json/put/test_vip_request_put_valid_file_with_two_group_user.json')

    def wtest__put_invalid_file_with_two_equal_group_user_(self):
        self.execute_some_put_verify_error(
            'api_vip_request/tests/json/put/test_vip_request_put_invalid_file_with_two_equal_group_user.json')

    def execute_some_put_verify_error(self, name_file):
        # update
        response = self.client.put(
            '/api/v3/vip-request/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code,
                         "Status code should be 400 and was %s" % response.status_code)

    def execute_some_put_verify_success(self, name_file):
        # update
        response = self.client.put(
            '/api/v3/vip-request/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # get datas updated
        response = self.client.get(
            '/api/v3/vip-request/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if datas were updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(response.data, sort_keys=True),
            "jsons should same"
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def execute_some_post_verify_error(self, name_file):
        # delete
        self.client.delete(
            '/api/v3/vip-request/1/',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # insert
        response = self.client.post(
            '/api/v3/vip-request/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code, "Status code should be 400 and was %s" % response.status_code)

        # try to get datas
        response = self.client.get(
            '/api/v3/vip-request/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(500, response.status_code, "Status code should be 500 and was %s" % response.status_code)

    def execute_some_post_verify_success(self, name_file):
        # insert
        response = self.client.post(
            '/api/v3/vip-request/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)

        # get data inserted
        response = self.client.get(
            '/api/v3/vip-request/{0}/'.format(response.data[0]['id']),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = response.data
        del data['vips'][0]['id']

        # test if data were inserted

        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            "jsons should same"
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # def test_get_success(self):
        #     """ test_get_success"""

        #     import time

        #     time.sleep(20)
        #     response = self.client.get(
        #         '/api/v3/vip-request/1/',
        #         content_type="application/json",
        #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        #     self.assertEqual(
        #         self.load_json_file('api_vip_request/tests/json/test_vip_request_get.json'),
        #         response.data
        #     )
        #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # def test_get_details_success(self):
        #     """ test_get_details_success"""
        #     response = self.client.get(
        #         '/api/v3/pool/details/1/',
        #         content_type="application/json",
        #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        #     log.info(response.data)
        #     self.assertEqual(
        #         self.load_json_file('api_pools/tests/json/test_pool_get_details.json'),
        #         response.data
        #     )
        #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # def test_put_success(self):
        #     """ test_put_success"""
        #     # update
        #     response = self.client.put(
        #         '/api/v3/pool/1/',
        #         data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put.json')),
        #         content_type="application/json",
        #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        #     # get datas updated
        #     response = self.client.get(
        #         '/api/v3/pool/1/',
        #         content_type="application/json",
        #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        #     # test if datas were updated
        #     self.assertEqual(
        #         self.load_json_file('api_pools/tests/json/test_pool_put.json'),
        #         response.data
        #     )
        #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # def test_post_success(self):
        #     """ test_post_success"""
        #     response = self.client.post(
        #         '/api/v3/pool/',
        #         data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_post.json')),
        #         content_type="application/json",
        #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        #     self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)
