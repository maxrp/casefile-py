# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from casefile import __version__

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='casefile',
    version=__version__,
    description='',
    long_description=readme,
    author='Max Parmer',
    author_email='maxp@trystero.is',
    url='https://github.com/maxrp/casefile-py',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

