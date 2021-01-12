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
# serializer_type='json-api' : Permet de serializer la reponse directement
# dans un data + format automatique pour un raise exception.

# Doc Entr'ouvert : authentificaiton pour utiliser les apis.
# https://doc-publik.entrouvert.com/tech/wcs/api-webservices/authentification/

# Doc Entr'ouvert : Récupération de coordonnées
# https://doc-publik.entrouvert.com/tech/wcs/api-webservices/recuperation-des-donnees-d-un-formulaire/

# Doc Entr'ouvert : Evolution du workflow
# https://doc-publik.entrouvert.com/tech/wcs/api-webservices/traitement-d-un-formulaire/
# https://doc-publik.entrouvert.com/tech/connecteurs/developpement-d-un-connecteur/#Journalisation

# import ast
try:
    import http.client
except ImportError:
    import httplib
import logging
import xmlrpc.client

from xmlrpc.client import ServerProxy
from django.db import models
from django.utils.translation import ugettext_lazy as _
from passerelle.base.models import BaseResource
from passerelle.compat import json_loads
from passerelle.utils.api import endpoint


class FileNotFoundError(Exception):
    http_status = 404


class ProxiedTransport(xmlrpc.client.Transport):
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

    healthsheet = None

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
    def test_connexion(self, request):
        """Display hello world if the connection with AES had been established"""
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
                "example_value": "22",
            }
        },
    )
    def get_child_health_sheet(self, request, child_id):
        """Return the health sheet's data of the child given

        :param request:
        :param child_id: int
            The child's identifier from AES
        :return:
        """
        if request.body:
            child = json_loads(request.body)
        else:
            child = dict([(x, request.GET[x]) for x in request.GET.keys()])
        child["id"] = child["child_id"]
        del child["child_id"]
        healthsheet = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_child_health_sheet",
            [child],
        )
        self.healthsheet = healthsheet
        return {"data": healthsheet}

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Recupere un attribut de la fiche sante",
        parameters={
            "child_id": {
                "description": "Identifiant d'un enfant",
                "example_value": "22",
            },
        },
    )
    def get_health_attribute(self, request, child_id):
        if self.healthsheet is None:
            self.healthsheet = self.get_child_health_sheet(request, child_id)
        return self.healthsheet.get("data")

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Recupere le blood type",
        parameters={
            "child_id": {
                "description": "Identifiant d'un enfant",
                "example_value": "22",
            }
        },
    )
    def get_blood_type(self, request, child_id):
        if self.healthsheet is None:
            self.healthsheet = self.get_child_health_sheet(request, id)
        return self.healthsheet.get("data").get("blood_type")

    @endpoint(
        serializer_type="json-api", perm="can_access", description="get allergies",
    )
    def get_allergies(self, request):
        """Get allergies from AES

        :param request:
        :return:
        """
        allergies = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_allergies",
            [],
        )
        return allergies

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Get all diseases from AES",
    )
    def get_disease(self, request):
        """ Get diseases from AES

        :param request:
        :return:
        """
        diseases = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_diseases",
            [],
        )
        return diseases

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Get natation levels from AES",
    )
    def get_swim_levels(self, request):
        """Get swimming levels from AES

        Swimming levels assess the child's ability to swim

        :param request:
        :return:
        """
        swim_level = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_swim_levels",
            [],
        )
        return swim_level

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Get doctors from AES",
    )
    def get_doctors(self, request):
        """Get doctors from AES

        :param request:
        :return:
        """
        doctors = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_doctors",
            [],
        )
        return doctors

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Get handicap levels from AES",
    )
    def get_handicap_levels(self, request):
        """Get handicap from AES

        :param request:
        :return:
        """
        handicap_levels = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "get_level_handicap",
            [],
        )
        return handicap_levels

    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Get country from AES",
    )
    def get_countries(self, request):
        """Get Countries from AES

        :param request:
        :return:
        """
        countries = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "res.country",
            "search_read",
            [],
            {"fields": ["id", "name"], "context": {"lang": "fr_BE"}},
        )
        for country in countries:
            country["text"] = country.pop("name")
        return {"data": countries}


    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        description="Propose la liste des options disponibles pour la fiche santé"
    )
    def get_healthsheet_options(self, request):
        """Display a datasource with all options of health sheet form

        :param request:
        :return:
        """
        healthsheet_options = [
            {'id': 'blood_type', 'text': 'Quel est le groupe sanguin de l\'enfant ?'},
            {'id': 'tetanos', 'text': 'L\'enfant a-t-il été vacciné contre le tétanos ?'},
            {'id': 'intervention', 'text': 'L\'enfant a-t-il subit une intervention récemment ?'},
            {'id': 'swim', 'text': 'L\'enfant sait-il nager ?'},
            {'id': 'handicap', 'text': 'L\'enfant souffre-t-il d\'un handicap ?'},
            {'id': 'activity_no_available', 'text': 'Activités non praticables'},
            {'id': 'regime', 'text': 'L\'enfant suit-il un régime spécifique ?'},
            {'id': 'arnica', 'text': 'Autorisez-vous les accompagnants à utiliser de l\'arnica ?'},
            {'id': 'allergies', 'text': 'L\'enfant a-t-il des allergies ?'},
            {'id': 'new_allergies', 'text': 'Permettre aux parents d\'ajouter d\'autres allergies ?'},
            {'id': 'diseases', 'text': 'L\'enfant a-t-il des maladies ?'},
            {'id': 'new_diseases', 'text': 'Permettre aux parents d\'ajouter d\'autres maladies ?'},
            {'id': 'medication', 'text': 'L\'enfant doit-il prendre des médicaments ?'},
            {'id': 'medical_data','text': 'Y a-t-il des données médicales spécifiques importantes à connaître pour le '
                                          'bon déroulement des activités (épilepsie,problème cardiaque, asthme, '
                                          '...) ?',
             'disabled': True},
            {'id': 'other_contact_address', 'text': 'Demander l\'adresse des autres contacts'},
            {'id': 'photo', 'text': 'L\'enfant peut-il être pris en photo durant les stages ou les plaines ?'},
            {'id': 'photo_general',
             'text': 'L\'enfant peut-il être pris en photo lors des garderies, ateliers, spectacles, ou autre ?'},
            {'id': 'facebook',
             'text': 'Les photos de l\'enfant peuvent-elles être publiées sur les réseaux sociaux (site de l\'école, '
                     'Facebook) ?'}, ]
        return {"data": healthsheet_options}


    @endpoint(
        serializer_type="json-api",
        perm="can_access",
        methods=["post", ],
        description="envoyer les donnees dans aes",
    )
    def post_child_health_sheet(self, request):
        """Post health sheet to AES to register it

        :param request:
        :return:
        """
        try:
            fields = json_loads(request.body)
        except ValueError as e:
            raise ValueError(e.message)
        is_update = self.get_aes_server().execute_kw(
            self.database_name,
            self.get_aes_user_id(),
            self.password,
            "aes_api.aes_api",
            "post_child_health_sheet",
            [fields],
        )
        return is_update
