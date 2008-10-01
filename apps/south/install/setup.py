#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name='South',
    version='0.3',
    description='South: Migrations for Django',
    author='Andrew Godwin & Andy McCurdy',
    author_email='south@aeracode.org',
    url='http://south.aeracode.org/',
    packages=["south", "south.db", "south.management", "south.management.commands", "south.tests"],
)
