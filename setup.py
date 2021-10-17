#!/usr/bin/env python3

from distutils.core import setup

setup(name='lictool',
      version='1.0',
      description='License Header Manager',
      author='Marius Zwicker',
      author_email='marius@numlz.de',
      url='https://github.com/emzeat/license-tools',
      packages=['license_tools'],
      package_data={'license_tools': ['license_tools/*.erb']},
      scripts=['lictool'],
      requires=['jinja2']
     )