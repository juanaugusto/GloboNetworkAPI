# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client
from mock import patch

from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.tests.pool_v3_deploy_test import MockPlugin
from networkapi.api_pools.tests.sorted_list_encoder_test import SortedListEncoder
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class PoolTestPostDeployV3Case(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')

    def tearDown(self):
        pass

    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def test_deploy_pool_not_deployed_success(self, test_patch):
        """
        It tests if the deploy of not deployed pool returns success suposing that equipments will act in the right way always
        """

        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        # deploy pool id=6 already present in test database
        response = self.client.post(
            '/api/v3/pool/deploy/6/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(200, response.status_code,
                         "Status code should be 200 and was %s" % response.status_code)

    # test will not ne executed by jenkins
    @patch('networkapi.plugins.factory.PluginFactory.factory')
    def wtest_deploy_pool_deployed_error(self, test_patch):
        """
        It tests if the deploy of a deployed pool returns fail suposing that equipments will act in the right way always
        """
        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/post/test_pool_post_valid_file_with_one_group_user.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        id_gerado = response.data[0]['id']
        # deploy pool id=7 already present in test database
        response = self.client.post(
            '/api/v3/pool/deploy/{0}/'.format(id_gerado),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        print id_gerado
        print (json.dumps(response.data, indent=4, sort_keys=True, cls=SortedListEncoder))

        response = self.client.get(
            '/api/v3/pool/details/{0}/'.format(id_gerado),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        mock = MockPlugin()
        mock.status(True)
        test_patch.return_value = mock

        response = self.client.post(
            '/api/v3/pool/deploy/' + str(id_gerado) + '/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        print (json.dumps(response.data, indent=4, sort_keys=True, cls=SortedListEncoder))
        self.assertEqual(400, response.status_code,
                         "Status code should be 400 and was %s" % response.status_code)


class PoolTestPostNotDeployV3Case(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def execute_some_post_detailed_verify_success(self, name_file):
        # insert
        response = self.client.post('/api/v3/pool/', data=json.dumps(self.load_json_file(name_file)),
                                    content_type="application/json",
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)

        data_to_insert = self.load_json_file(name_file)
        # insert Administradores group into json
        if not any(1 in d.values() for d in data_to_insert['server_pools'][0]['groups_permissions']):
            data_to_insert['server_pools'][0]["groups_permissions"].append({"read": True,
                                                                            "write": True,
                                                                            "change_config": True,
                                                                            "group": 1,
                                                                            "delete": True})

        # get data inserted
        response = self.client.get('/api/v3/pool/details/' + str(response.data[0]['id']) + '/',
                                   content_type="application/json",
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = response.data
        del data['server_pools'][0]['id']
        del data['server_pools'][0]["servicedownaction"]["type"]
        data['server_pools'][0]["environment"] = data['server_pools'][0]["environment"]["id"]

        for i in range(0, len(data['server_pools'][0]["groups_permissions"])):
            data['server_pools'][0]["groups_permissions"][i]["group"] = \
                data['server_pools'][0]["groups_permissions"][i]["group"]["id"]

        # test if data were inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # test if inserted data is equals to the data that is being received
        self.assertEqual(json.dumps(data_to_insert, sort_keys=True, cls=SortedListEncoder),
                         json.dumps(data, sort_keys=True, cls=SortedListEncoder), "jsons should same")

    def execute_some_post_verify_error(self, name_file, expected_insert_error_code=400):
        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(expected_insert_error_code, response.status_code,
                         "Status code should be %s and was %s" % (expected_insert_error_code, response.status_code))

    def execute_some_post_verify_success(self, name_file):
        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)

        # get data inserted
        response = self.client.get(
            '/api/v3/pool/' + str(response.data[0]['id']) + '/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = response.data

        del data['server_pools'][0]['id']

        # test if data were inserted
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            "jsons should same"
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_post_valid_file(self):
        """ test_post_valid_file"""
        self.execute_some_post_verify_success('api_pools/tests/json/post/test_pool_post_valid_file.json')

    def test_post_out_of_range_port(self):
        """ test_post_out_of_range_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_out_of_range_port.json')

    def test_post_negative_port(self):
        """ test_post_negative_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_port.json')

    def test_post_float_port(self):
        """ test_post_float_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_float_port.json')

    def test_post_zero_port(self):
        """ test_post_zero_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_zero_port.json')

    def test_post_string_port(self):
        """ test_post_string_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_string_port.json')

    def test_post_float_environment(self):
        """ test_post_float_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_float_environment.json')

    def test_post_string_environment(self):
        """ test_post_string_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_string_environment.json')

    def test_post_zero_environment(self):
        """ test_post_zero_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_zero_environment.json')

    def test_post_negative_environment(self):
        """ test_post_negative_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_environment.json')

    def test_post_integer_name_servicedownaction(self):
        """ test_post_integer_name_servicedownaction"""
        self.execute_some_post_verify_error(
            'api_pools/tests/json/post/test_pool_post_integer_name_servicedownaction.json')

    def test_post_invalid_healthcheck_type(self):
        """ test_post_invalid_healthcheck_type"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_invalid_healthcheck_type.json')

    def test_post_invalid_destination(self):
        """ test_post_invalid_destination"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_invalid_destination.json')

    def test_post_negative_default_limit(self):
        """ test_post_negative_default_limit"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_default_limit.json')

    def test_post_integer_lb_method(self):
        """ test_post_integer_lb_method"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_integer_lb_method.json')

    def test_post_string_id_servicedownaction(self):
        """  test_post_string_id_servicedownaction"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_string_id_servicedownaction.json')

    def test_post_zero_id_servicedownaction(self):
        """  test_post_zero_id_servicedownaction"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_zero_id_servicedownaction.json')

    def test_post_negative_id_servicedownaction(self):
        """  test_post_negative_id_servicedownaction"""
        self.execute_some_post_verify_error(
            'api_pools/tests/json/post/test_pool_post_negative_id_servicedownaction.json')

    def test_post_valid_file_with_one_group_user(self):
        self.execute_some_post_detailed_verify_success(
            'api_pools/tests/json/post/test_pool_post_valid_file_with_one_group_user.json')

    def test_post_valid_file_with_two_group_user(self):
        self.execute_some_post_detailed_verify_success(
            'api_pools/tests/json/post/test_pool_post_valid_file_with_two_group_user.json')

    def test_post_invalid_file_with_two_equal_group_user(self):
        self.execute_some_post_verify_error(
            'api_pools/tests/json/post/test_pool_post_invalid_file_with_two_equal_group_user.json', 500)
