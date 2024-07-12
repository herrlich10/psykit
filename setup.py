#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# Direct import is usually not possible because psychopy is not in the environment

setup(
    name="psykit",
    version=open('psykit/__version__').read().strip(),
    author="herrlich10",
    author_email="herrlich10@gmail.com",
    description="A PsychoPy extension for stereoscopic display and more.",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url="https://github.com/herrlich10/psykit",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)