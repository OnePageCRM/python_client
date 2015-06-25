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
    name="onepagecrm-python",
    version="0.1.0",
    license="MIT",
    description="Connect and interface with the OnePageCRM REST API",
    long_description=read("README.rst"),
    author="Ruairi Fahy",
    author_email="devteam@onepagecrm.com",
    url="https://github.com/onepagecrm/python-client",
    packages=find_packages("onepagecrm"),
    package_dir={"": "onepagecrm"},
    py_modules=[splitext(basename(i))[0] for i in glob.glob("onepagecrm/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    keywords=[
        'onepagecrm',
    ],
    install_requires=[
        "requests"
    ]
)
