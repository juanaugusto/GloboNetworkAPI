# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import uuid
import threading
from django.db import models
from datetime import datetime
from networkapi.models.BaseModel import BaseModel
from networkapi.usuario.models import Usuario

from django.utils.translation import ugettext_lazy as _

class EventLogError(Exception):

    """Representa um erro ocorrido durante acesso à tabela event_log."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class EventLog(BaseModel):

    ADD = 0
    CHANGE = 1
    DELETE = 2

    id = models.AutoField(primary_key=True, db_column='id_evento')
    usuario = models.ForeignKey(Usuario, db_column='id_user')
    hora_evento = models.DateTimeField()
    acao = models.TextField()
    funcionalidade = models.TextField()
    parametro_anterior = models.TextField()
    parametro_atual = models.TextField()
    evento = models.TextField()
    resultado = models.IntegerField()
    id_objeto = models.IntegerField()

    logger = logging.getLogger('EventLog')

    class Meta(BaseModel.Meta):
        db_table = u'event_log'
        managed = True

    @classmethod
    def log(cls, usuario, evento):
        """
        saves the eventlog in the database
        @params
        usuario: Usuario object
        evento: dict in the form
        {
            "acao": value,
            "funcionalidade": value,
            "parametro_anterior": value,
            "parametro_atual": value,
            "id_objeto": value,
            "audit_request": value
        }
        """

        try:
            functionality = Functionality()
            event_log = EventLog()
            event_log.usuario = usuario
            event_log.hora_evento = datetime.now()
            event_log.acao = evento['acao']
            event_log.funcionalidade = functionality.exist(
                evento['funcionalidade'])
            event_log.parametro_anterior = evento['parametro_anterior']
            event_log.parametro_atual = evento['parametro_atual']
            event_log.id_objeto = evento['id_objeto']
            event_log.evento = ''
            event_log.resultado = 0
            event_log.save(usuario)
        except Exception, e:
            cls.logger.error(
                u'Falha ao salvar o log: evento = %s, id do usuario = %s.' % (evento, usuario.id))
            raise EventLogError(
                e, u'Falha ao salvar o log: evento = %s, id do usuario = %s.' % (evento, usuario.id))

    @classmethod
    def uniqueUsers(cls):
        userlist = Usuario.objects.all().order_by('user')

        return userlist

class AuditRequest(models.Model):
    """
    copied from https://github.com/leandrosouza/django-simple-audit
    """

    THREAD_LOCAL = threading.local()

    request_id = models.CharField(max_length=255)
    ip = models.IPAddressField()
    path = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))
    user = models.ForeignKey(Usuario)

    class Meta:
        db_table = u'audit_request'

    @staticmethod
    def new_request(path, user, ip):
        """
        Create a new request from a path, user and ip and put it on thread context.
        The new request should not be saved until first use or calling method current_request(True)
        """
        audit_request = AuditRequest()
        audit_request.ip = ip
        audit_request.user = user
        audit_request.path = path
        audit_request.request_id = uuid.uuid4().hex
        while AuditRequest.objects.filter(request_id=audit_request.request_id).exists():
            audit_request.request_id = uuid.uuid4().hex

        AuditRequest.THREAD_LOCAL.current = audit_request
        return audit_request

    @staticmethod
    def set_request_from_id(request_id):
        """ Load an old request from database and put it again in thread context. If request_id doesn't
        exist, thread context will be cleared """
        audit_request = None
        if request_id is not None:
            try:
                audit_request = AuditRequest.objects.get(request_id=request_id)
            except AuditRequest.DoesNotExist:
                pass

        AuditRequest.THREAD_LOCAL.current = audit_request

    @staticmethod
    def current_request(force_save=False):
        """ Get current request from thread context (or None doesn't exist). If you specify force_save,
        current request will be saved on database first.
        """
        audit_request = getattr(AuditRequest.THREAD_LOCAL, 'current', None)
        if force_save and audit_request is not None and audit_request.pk is None:
            audit_request.save()
        return audit_request

    @staticmethod
    def cleanup_request():
        """
        Remove audit request from thread context
        """
        AuditRequest.THREAD_LOCAL.current = None

class Functionality(models.Model):
    nome = models.CharField(
        max_length=50, primary_key=True, db_column='functionality')

    logger = logging.getLogger('Funcionality')

    class Meta:
        db_table = u'functionality'

    @classmethod
    def exist(cls, event_functionality):
        func = Functionality.objects.filter(nome=event_functionality)
        if func.exists():
            return event_functionality
        else:
            functionality = Functionality()
            functionality.nome = event_functionality
            functionality.save()
            return event_functionality
