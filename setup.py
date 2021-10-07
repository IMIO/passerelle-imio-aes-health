#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import re
import subprocess
import sys

from setuptools.command.install_lib import install_lib as _install_lib
from distutils.command.build import build as _build
from distutils.command.sdist import sdist
from distutils.cmd import Command
from setuptools import setup, find_packages


class compile_translations(Command):
    description = "compile message catalogs to MO files via django compilemessages"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            from django.core.management import call_command

            for path, dirs, files in os.walk("passerelle_imio_aes_health"):
                if "locale" not in dirs:
                    continue
                curdir = os.getcwd()
                os.chdir(os.path.realpath(path))
                call_command("compilemessages")
                os.chdir(curdir)
        except ImportError:
            sys.stderr.write("!!! Please install Django >= 1.4 to build translations\n")


class build(_build):
    sub_commands = [("compile_translations", None)] + _build.sub_commands


class install_lib(_install_lib):
    def run(self):
        self.run_command("compile_translations")
        _install_lib.run(self)


version = "0.1.15"

setup(
    name="passerelle-imio-aes-health",
    version=version,
    author="Christophe Boulanger",
    author_email="christophe.boulanger@imio.be",
    packages=find_packages(),
    include_package_data=True,
    url="https://dev.entrouvert.org/projects/imio/",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "django >=1.11, <2.3",
    ],
    zip_safe=False,
    cmdclass={
        "build": build,
        "compile_translations": compile_translations,
        "install_lib": install_lib,
        "sdist": version,
    },
)
