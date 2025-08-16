# license.py
#
# Copyright (c) 2012 - 2025 Marius Zwicker
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

"""
Enumeration of available licenses
"""

import pathlib

BASE_DIR = pathlib.Path(__file__).parent
SPDX_LICENSES = list(BASE_DIR.glob('spdx_licenses/*.spdx'))
OTHER_LICENSES = list(BASE_DIR.glob('other_licenses/*.license'))
LICENSES = {license_file.stem: license_file for license_file in SPDX_LICENSES + OTHER_LICENSES}


class License:
    """Describes a license to be added to a header"""

    def __init__(self, builtin: str = None, custom: str = None):
        """
        Creates a new license

        Either builtin or custom need to be specified.

        :builtin: One of the supported licenses, see LICENSES
        :custom: Configures a custom license text
        """
        if builtin:
            self.name = builtin
            self.header = LICENSES.get(builtin, None)
            if self.header is None:
                raise TypeError(f"No such license '{builtin}'")
            self.builtin = True
            self.spdx = self.header in SPDX_LICENSES
            self.header = self.header.parent.name + '/' + self.header.name
        elif custom:
            self.name = 'custom'
            self.header = custom
            self.builtin = False
            self.spdx = False
        else:
            raise KeyError("Need to select a 'builtin' or provide 'custom' license")
