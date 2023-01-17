"""
 setup.py

 Copyright (c) 2021 - 2023 Marius Zwicker
 All rights reserved.

 SPDX-License-Identifier: GPL-2.0-or-later

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Library General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

#!/usr/bin/env python3

from distutils.core import setup
from subprocess import check_output, CalledProcessError
import re
import os

GIT_DESCRIBE = 'git describe --tags --long --dirty'
GIT_RE = r'^v(?P<tag>.+?)-(?P<commits>[0-9]+)-g(?P<sha>[a-z0-9]{7,40}?)(?P<dirty>-dirty)?$'

try:
    git_describe = check_output(GIT_DESCRIBE.split(' '), encoding='utf8', cwd=os.path.dirname(__file__)).strip()
    match = re.match(GIT_RE, git_describe)
    tag = match.group('tag')
    commits = match.group('commits')
    sha = match.group('sha')
    dirty = match.lastgroup == 'dirty'

    # git describe will be something like <tag>-<commits>-g<sha>-dirty, convert this to https://semver.org
    meta = []
    if int(commits) > 0:
        meta.append(f'{commits}.sha.{sha}')
    if dirty:
        meta.append('dirty')
    if meta:
        GIT_VERSION = f"{tag}+{'.'.join(meta)}"
    else:
        GIT_VERSION = tag

except CalledProcessError:
    GIT_VERSION = '0.0'
except AttributeError:
    GIT_VERSION = '0.0'

setup(name='mz-lictools',
      version=GIT_VERSION,
      description='License Header Manager',
      author='Marius Zwicker',
      author_email='marius@numlz.de',
      url='https://github.com/emzeat/mz-lictools',
      packages=['license_tools'],
      package_data={'license_tools': ['*.license', '*.spdx', '*.j2']},
      entry_points={
          'console_scripts': ['lictool=license_tools:main']
      },
      install_requires=['jinja2']
      )
