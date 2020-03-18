#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016  Entr'ouvert
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Decorateurs des endpoints:
# serializer_type='json-api' : Permet de serializer la reponse directement dans un data + format automatique pour un raise exception.

# Doc Entr'ouvert : authentificaiton pour utiliser les apis.
# https://doc-publik.entrouvert.com/tech/wcs/api-webservices/authentification/

# Doc Entr'ouvert : Récupération de coordonnées
# https://doc-publik.entrouvert.com/tech/wcs/api-webservices/recuperation-des-donnees-d-un-formulaire/

# Doc Entr'ouvert : Evolution du workflow
# https://doc-publik.entrouvert.com/tech/wcs/api-webservices/traitement-d-un-formulaire/
# https://doc-publik.entrouvert.com/tech/connecteurs/developpement-d-un-connecteur/#Journalisation

# import ast
import httplib
import json
import logging
import requests
import urllib
import xmlrpclib

from xmlrpclib import ServerProxy
from django.db import models
from django.utils.translation import ugettext_lazy as _
from passerelle import settings
from passerelle.base.models import BaseResource
from passerelle.utils.api import endpoint


class FileNotFoundError(Exception):
    http_status = 404


class ProxiedTransport(xmlrpclib.Transport):
    def set_proxy(self, proxy):
        self.proxy = proxy

    def make_connection(self, host):
        self.realhost = host
        h = httplib.HTTPConnection(self.proxy)
        return h

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", "http://%s%s" % (self.realhost, handler))

    def send_host(self, connection, host):
        connection.putheader("Host", self.realhost)


logger = logging.getLogger(__name__)


class IImioAesHealth(BaseResource):
    server_url = models.CharField(
        max_length=128,
        blank=False,
        verbose_name=_("SERVER URL"),
        help_text=_("SERVER URL"),
    )
    username = models.CharField(max_length=128, blank=True, verbose_name=_("Username"))
    password = models.CharField(max_length=128, blank=True, verbose_name=_("Password"))
    database_name = models.CharField(
        max_length=128, blank=False, verbose_name=_("Database name")
    )

    category = _("Business Process Connectors")
    api_description = "Ce connecteur propose les méthodes d'échanges avec le produit IA-AES. (partie fiche santé)"

    class Meta:
        verbose_name = _("i-ImioAesHealth")

    @classmethod
    def get_verbose_name(cls):
        return cls._meta.verbose_name

    def get_aes_user_id(self):
        server = ServerProxy("{}/xmlrpc/2/common".format(self.server_url))
        try:
            user_id = server.authenticate(
                self.database_name, self.username, self.password, {}
            )
        except Exception as e:
            self.logger.error(
                "get_aes_user_id : server.authenticate error : {}".format(str(e))
            )
            raise
        return user_id

    def get_aes_server(self):
        server = ServerProxy(
            "{}/xmlrpc/2/object".format(self.server_url), allow_none=True
        )
        return server

    def get_aes_report(self):
        report = ServerProxy("{}/xmlrpc/2/report".format(self.server_url))
        return report

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Tester la connexion avec AES",
    )
    def tst_connexion(self, request):
        test = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "hello_world",
            [],
        )
        return test

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Récupération de la fiche santé d'un enfant",
        parameters={
            "child_id": {
                "description": "Identifiant d'un enfant",
                "example_value": "786",
            }
        },
    )
    def get_child_health_sheet(self, request):
        # child = {"id": request.GET["child_id"]}
        if request.body:
            child = json.loads(request.body)
        if not child.has_key["child_id"]:
            return False

ll
health_sheet = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_child_health_sheet",
            [child],
        )
        return {"data": health_sheet}

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Récupérer les enfants pour le parent connecté",
        parameters={
            "email": {
                "description": "Adresse e-mail d'un parent AES/TS",
                "example_value": "demotsaes@imio.be",
            }
        },
    )
    def get_children(self, request):
        # parent = {"email": request.GET["email"]}
        if request.body:
            parent = json.loads(request.body)
        if parent["email"] == "":
            return False
        try:
            children = self.get_aes_server().execute_kw(
                self.database_name,
                self.get_aes_user_id(),
                self.password,
                "aes_api.aes_api",
                "get_children",
                [parent],
            )
            return children
        except Exception:
            return False

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Vérifier qu'un parent existe bien dans AES",
        parameters={
            "email": {
                "description": "Adresse e-mail du parent",
                "example_value": "demotsaes@imio.be",
            },
            "nrn": {
                "description": "Numéro de registre national du parent",
                "example_value": "00000000097",
            },
        },
    )
    def is_registered_parent(self, request):
        r = requests.get(
            "{}/api/users/?email={}".format(
                settings.AUTHENTIC_URL, urllib.quote_plus(request.GET["email"])
            ),
            auth=(settings.AES_LOGIN, settings.AES_PASSWORD),
        )
        nrn = (
            r.json().get("results")[0].get("niss")
            if r is not None
            else request.GET["nrn"]
        )
        parent = {"email": request.GET["email"], "nrn": nrn}
        if parent["email"] == "":
            return False
        is_registered_parent = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "is_registered_parent",
            [parent],
        )
        return is_registered_parent
