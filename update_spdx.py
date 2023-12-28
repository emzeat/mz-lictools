# update_spdx.py
#
# Copyright (c) 2023 Marius Zwicker
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

'''
Helper to automatically pull and sync the list of available SPDX licenses
from https://github.com/spdx/license-list-data and documented at
https://github.com/spdx/license-list-data/blob/main/accessingLicenses.md#programmatically-accessing-the-online-license-list-using-json
'''

import pathlib
import textwrap
import requests

LICENSE_LIST_DATA_REPO = 'https://github.com/spdx/license-list-data'
SPDX_FOLDER = pathlib.Path(__file__).parent / 'license_tools'
BLACKLIST = {
    'CPAL-1.0'  # using too many variables to be added automatically
    'CUA-OPL-1.0',
    'LLPL-1.3c',
    'MPL-1.0',
    'MPL-1.1',
    'RPSL-1.0',
    'SISSL',
    'SPL-1.0',
    'MulanPSL-2.0',
    'OCLC-2.0'
}

licenses = requests.get(f'{LICENSE_LIST_DATA_REPO}/raw/main/json/licenses.json')
licenses = licenses.json()

for license in licenses['licenses']:
    id = license['licenseId']
    if id in BLACKLIST:
        continue
    license_spdx = SPDX_FOLDER / f'{id}.spdx'
    if license_spdx.exists() and license_spdx.read_text():
        # retain existing headers
        continue
    osi = license.get('isOsiApproved', True)
    deprecated = license.get('isDeprecatedLicenseId', False)
    if osi and not deprecated:
        detail = requests.get(f'{LICENSE_LIST_DATA_REPO}/raw/main/json/details/{id}.json')
        detail = detail.json()
        header = detail.get('standardLicenseHeaderTemplate', None)
        if not header:
            header = detail.get('standardLicenseHeader', None)
        if not header:
            # no standard header defined, use name
            header = [f"Licensed under the {detail['name']}"]
        else:
            header = header.strip('"\n\r')
            header = header.split('\n')

            def filter_tags(line):
                '''Returns false if a copyright or tag line'''
                if line.lower().startswith('copyright'):
                    return False
                if line.startswith('<<') and line.endswith('>>'):
                    return False
                return True

            def replace_tags(string, replacement=''):
                '''Replaces <<beginOptional>>...<<endOptional>> tags'''
                i = 0
                while i < len(string):
                    i = string.find('<<begin', i)
                    if i < 0:
                        break
                    j = string.find('<<end', i)
                    if j < 0:
                        break
                    j = string.find('>>', j) + 2
                    string = string[:i] + replacement + string[j:]
                return string

            def pad_url(string):
                '''Pads urls to obtain a license'''
                if string.startswith('http'):
                    return f'\n    {string.strip()}\n'
                return string
            header = [h for h in header if filter_tags(h) and h]
            header = [replace_tags(h) for h in header]
            header = ['\n'.join(textwrap.wrap(h, 72)) + '\n' if len(h) > 72 else h for h in header]
            header = [pad_url(h) for h in header]

        print(f"-- {id}")
        TEMPLATE_HEADER = '\n'.join(header)
        license_spdx.write_text(TEMPLATE_HEADER.strip() + '\n')
