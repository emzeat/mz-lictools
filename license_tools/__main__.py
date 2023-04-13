#
# __main__.py
#
# Copyright (c) 2012 - 2023 Marius Zwicker
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
See README.md for detail and documentation
"""

import sys
import license_tools

if __name__ == "__main__":
    try:
        license_tools.main()
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        sys.exit(1)
