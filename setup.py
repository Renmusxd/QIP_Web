# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='QIP_Web',
    version='0.1',
    python_requires='>3.4',
    description='Quantum Computing Library Monitoring Server',
    long_description='A webserver to monitor distributed QIP managers and workers.',
    author='Sumner Hearth',
    author_email='sumnernh@gmail.com',
    license='MIT',
    packages=find_packages(),
    requires=['qip', 'flask', 'protobuf'],
)
