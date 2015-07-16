# -*- encoding: utf8 -*-
import glob
import io
import re
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()

setup(
    name="onepagecrm",
    version="0.1.0",
    license="MIT",
    description="Connect and interface with the OnePageCRM REST API",
    author="Ruairi Fahy",
    author_email="devteam@onepagecrm.com",
    url="https://github.com/onepagecrm/python-client",
    packages=["onepagecrm"],
    install_requires=[
        "requests",
    ]
)
