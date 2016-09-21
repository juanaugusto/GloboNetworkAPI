# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.api_pools.tests.sorted_list_encoder_test import SortedListEncoder
from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolTestPutV3Case(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_valid_file_with_one_group_user(self):
        self.execute_some_put_detailed_verify_success(
            'api_pools/tests/json/put/test_pool_put_valid_file_with_one_group_user.json')

    def test_put_valid_file_with_two_group_user(self):
        self.execute_some_put_detailed_verify_success(
            'api_pools/tests/json/put/test_pool_put_valid_file_with_two_group_user.json')

    def test_put_invalid_file_with_two_equal_group_user(self):
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_invalid_file_with_two_equal_group_user.json',
            expected_status_code=500)

    def test_put_valid_file(self):
        """ test_put_valid_file"""
        self.execute_put_verify_success(
            'api_pools/tests/json/put/test_pool_put_valid_file.json')

    def test_put_out_of_range_port(self):
        """ test_put_out_of_range_port"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_out_of_range_port.json')

    def test_put_negative_port(self):
        """ test_put_negative_port"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_port.json')

    def test_put_float_port(self):
        """ test_put_float_port"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_float_port.json')

    def test_put_zero_port(self):
        """ test_put_zero_port"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_zero_port.json')

    def test_put_string_port(self):
        """ test_put_string_port"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_string_port.json')

    def test_put_float_environment(self):
        """ test_put_float_environment"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_float_environment.json')

    def test_put_string_environment(self):
        """ test_put_string_environment"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_string_environment.json')

    def test_put_zero_environment(self):
        """ test_put_zero_environment"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_zero_environment.json')

    def test_put_negative_environment(self):
        """ test_put_negative_environment"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_environment.json')

    def test_put_integer_name_servicedownaction(self):
        """ test_put_integer_name_servicedownaction"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_integer_name_servicedownaction.json')

    def test_put_invalid_healthcheck_type(self):
        """ test_put_invalid_healthcheck_type"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_invalid_healthcheck_type.json')

    def test_put_invalid_destination(self):
        """ test_put_invalid_destination"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_invalid_destination.json')

    def test_put_negative_default_limit(self):
        """ test_put_negative_default_limit"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_default_limit.json')

    def test_put_integer_lb_method(self):
        """ test_put_integer_lb_method"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_integer_lb_method.json')

    def test_put_string_id_servicedownaction(self):
        """  test_put_string_id_servicedownaction"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_string_id_servicedownaction.json')

    def test_put_zero_id_servicedownaction(self):
        """  test_put_zero_id_servicedownaction"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_zero_id_servicedownaction.json')

    def test_put_negative_id_servicedownaction(self):
        """  test_put_negative_id_servicedownaction"""
        self.execute_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_id_servicedownaction.json')

    def execute_put_verify_error(self, name_file, expected_status_code=400):
        # update
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(expected_status_code, response.status_code,
                         "Status code should be %s and was %s" % (expected_status_code, response.status_code))

    def execute_put_verify_success(self, name_file):
        # update
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # get updated data
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if datas were updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(response.data, sort_keys=True),
            "jsons should be equal"
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def execute_some_put_detailed_verify_success(self, name_file):
        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file.replace('put', 'post'))),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)

        id_gerado = response.data[0]['id']
        # testando get
        response = self.client.get(
            '/api/v3/pool/details/' + str(id_gerado) + '/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data_to_insert = self.load_json_file(name_file)
        data_to_insert['server_pools'][0]['id'] = id_gerado
        # insert
        response = self.client.put('/api/v3/pool/' + str(id_gerado) + '/', data=json.dumps(data_to_insert),
                                   content_type="application/json",
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 201 and was %s" % response.status_code)

        # get inserted data
        response = self.client.get('/api/v3/pool/details/' + str(id_gerado) + '/',
                                   content_type="application/json",
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = response.data
        del data['server_pools'][0]["servicedownaction"]["type"]

        data['server_pools'][0]["environment"] = data['server_pools'][0]["environment"]["id"]

        for i in range(0, len(data['server_pools'][0]["groups_permissions"])):
            data['server_pools'][0]["groups_permissions"][i]["group"] = \
                data['server_pools'][0]["groups_permissions"][i]["group"]["id"]

        del data_to_insert['server_pools'][0]["permissions"]
        # insert Administradores group into json
        if not any(1 in d.values() for d in data_to_insert['server_pools'][0]['groups_permissions']):
            data_to_insert['server_pools'][0]["groups_permissions"].append({"read": True,
                                                                            "write": True,
                                                                            "change_config": True,
                                                                            "group": 1,
                                                                            "delete": True})
        # test if data were inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # test if inserted data is equals to the data that is being received
        self.assertEqual(json.dumps(data_to_insert, sort_keys=True, cls=SortedListEncoder),
                         json.dumps(data, sort_keys=True, cls=SortedListEncoder), "jsons should same")
