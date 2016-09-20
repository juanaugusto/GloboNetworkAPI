# -*- coding:utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns(
    'networkapi.api_healthcheck.views',
    url(r'^healthcheck/insert/$', 'insert'),  # TODO doc
)
