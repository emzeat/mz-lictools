#!/usr/bin/env python3
#
# setup.py
#
# Copyright (c) 2021 - 2023 Marius Zwicker
# All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Setup description for license_tools.

See README.md for detail and documentation.
"""

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
