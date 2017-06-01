# -*- coding: utf-8 -*-
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

import glob
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from networkapi.api_rack.permissions import Read, Write
from networkapi.api_rack import facade, exceptions
from networkapi.api_rack.serializers import RackSerializer, DCSerializer, DCRoomSerializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.system.facade import get_value as get_variable
from networkapi.system.facade import save_variable as save_variable
from django.core.exceptions import ObjectDoesNotExist
from networkapi.system import exceptions as var_exceptions
from networkapi.equipamento.models import Equipamento, EquipamentoAmbiente
from networkapi.rack.models import Rack, Datacenter, DatacenterRooms
import commands

log = logging.getLogger(__name__)


@permission_classes((IsAuthenticated, Write))
class RackView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("New Rack")


            if not request.DATA.get('rack'):
                raise exceptions.InvalidInputException()

            rack = facade.save_rack_dc(request.DATA.get('rack'))


            data = dict()
            rack_serializer = RackSerializer(rack)
            data['rack'] = rack_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()

    def get(self, user, *args, **kwargs):
        """Handles GET requests to list all Racks
        URLs: /api/rack/list/all/
        """

        try:
            log.info('List all Racks')

            data = dict()
            racks = Rack.objects.all().order_by('numero')

            data['racks'] = RackSerializer(racks, many=True).data if racks else list()

            return Response(data, status=status.HTTP_200_OK)

        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()



class RackDeployView(APIView):

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def post(self, *args, **kwargs):
        try:
            log.info('RACK deploy.')

            rack_id = kwargs.get('rack_id')
            rack = facade.get_by_pk(self.request.user, rack_id)

            try:
                PATH_TO_ADD_CONFIG = get_variable('path_to_add_config')
                REL_PATH_TO_ADD_CONFIG = get_variable('rel_path_to_add_config')
            except ObjectDoesNotExist:
                raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável PATH_TO_ADD_CONFIG ou "
                                                                   "REL_PATH_TO_ADD_CONFIG.")


            path_config = PATH_TO_ADD_CONFIG + '*' + rack.nome + '*'
            arquivos = glob.glob(path_config)

            # Get all files and search for equipments of the rack
            for var in arquivos:
                filename_equipments = var.split('/')[-1]
                rel_filename = "../../" + REL_PATH_TO_ADD_CONFIG + filename_equipments
                # Check if file is config relative to this rack
                if rack.nome in filename_equipments:
                    # Apply config only in spines. Leaves already have all necessary config in startup
                    if "ADD" in filename_equipments:
                        # Check if equipment in under maintenance. If so, does not aplly on it

                        equipment_name = filename_equipments.split('-ADD-')[0]
                        try:
                            equip = Equipamento.get_by_name(equipment_name)
                            if not equip.maintenance:
                                (erro, result) = commands.getstatusoutput("/usr/bin/backuper -T acl -b %s -e -i %s -w "
                                                                          "300" % (rel_filename, equipment_name))
                                if erro:
                                    raise exceptions.RackAplError()
                        except exceptions.RackAplError, e:
                            raise e
                        except:
                            # Error equipment not found, do nothing
                            pass

            # Create Foreman entries for rack switches
            facade.api_foreman(rack)

            datas = dict()
            success_map = dict()

            success_map['rack_conf'] = True
            datas['sucesso'] = success_map

            return Response(datas, status=status.HTTP_201_CREATED)

        except exceptions.RackNumberNotFoundError, exception:
            log.exception(exception)
            raise exceptions.RackNumberNotFoundError()
        except var_exceptions.VariableDoesNotExistException, exception:
            log.error(exception)
            raise var_exceptions.VariableDoesNotExistException(
                'Erro buscando a variável PATH_TO_ADD_CONFIG ou REL_PATH_TO_ADD_CONFIG.')
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException(exception)


class RackConfigView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("Gerando o arquivo de configuracao dos equipamentos do rack")

            if not request.DATA.get('racks'):
                raise exceptions.InvalidInputException()

            rack = facade.gerar_arquivo_config(request.DATA.get('racks'))

            data = dict()

            return Response(data, status=status.HTTP_201_CREATED)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()


class RackEnvironmentView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            log = logging.getLogger('Alocando ambientes e vlans do rack')

            if not request.DATA.get('racks'):
                raise exceptions.InvalidInputException()

            # Validar configuracao
            response = list()
            for rack in request.DATA.get('racks'):
                response.append(facade.rack_environments_vlans(rack, request.user))

            data = dict()

            return Response(data, status=status.HTTP_200_OK)

        except Exception, e:
            raise Exception("Os ambientes e Vlans não foram alocados. Erro: %s" % e)


class DataCenterView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("Datacenter")

            if not request.DATA.get('dc'):
                raise exceptions.InvalidInputException()

            dc = facade.save_dc(request.DATA.get('dc'))
            dc_serializer = DCSerializer(dc)

            data = dict()
            data['dc'] = dc_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()


class FabricView(APIView):

    @commit_on_success
    def post(self, request, *args, **kwargs):
        try:
            log.info("Post - Fabric")

            if not request.DATA.get('dcrooms'):
                raise exceptions.InvalidInputException()

            dcrooms = facade.save_dcrooms(request.DATA.get('dcrooms'))

            data = dict()
            dcroom_serializer = DCRoomSerializer(dcrooms)
            data['dcroom'] = dcroom_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()

    @commit_on_success
    def put(self, request, *args, **kwargs):
        try:
            log.info("Put - Fabric")

            if not request.DATA.get('fabric'):
                raise exceptions.InvalidInputException()
            #validar o json

            fabric_id = kwargs.get('fabric_id')
            fabric = request.DATA.get('fabric')

            if fabric.get("flag"):
                dcrooms = facade.update_fabric_config(fabric_id, fabric)
            else:
                dcrooms = facade.edit_dcrooms(fabric_id, fabric)

            dcroom_serializer = DCRoomSerializer(dcrooms)
            data = dict()
            data['dcroom'] = dcroom_serializer.data

            return Response(data, status=status.HTTP_200_OK)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()