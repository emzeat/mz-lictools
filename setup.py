#
# setup.py
#
# Copyright (c) 2021 Marius Zwicker
# All rights reserved.
#
# @LICENSE_HEADER_START@
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# @LICENSE_HEADER_END@
#

#!/usr/bin/env python3

from distutils.core import setup

setup(name='lictool',
      version='1.0',
      description='License Header Manager',
      author='Marius Zwicker',
      author_email='marius@numlz.de',
      url='https://github.com/emzeat/license-tools',
      packages=['license_tools'],
      package_data={'license_tools': ['*.erb', '*.j2']},
      scripts=['lictool'],
      requires=['jinja2']
      )
