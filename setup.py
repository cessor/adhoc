#!/usr/bin/env python

from distutils.core import setup

setup(
    name='blockhosts',
    version='1.0',
    description='Blocks Hosts',
    author='Johannes Hofmeister',
    author_email='py_blockhosts@spam.cessor.de',
    url='https://github.com/cessor/blockhosts/',
    packages=['blockhosts'],
    scripts=['scripts/blockhosts',
             'scripts/block',
             'scripts/unblock',
             'scripts/blockhosts.bat',
             'scripts/block.bat',
             'scripts/unblock.bat']
)
