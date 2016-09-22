# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolTestGeneralV3Case(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass
