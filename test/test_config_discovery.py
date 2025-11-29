# test.py
#
# Copyright (c) 2021 - 2025 Marius Zwicker
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

import unittest
import tempfile
import license_tools
from pathlib import Path


class TestConfigDiscovery(unittest.TestCase):

    def test_single_config_in_root(self):
        with tempfile.TemporaryDirectory() as test_dir:
            test_dir = Path(test_dir)

            config = test_dir / license_tools.LICENSE_JSON
            config.write_text("{}")

            subdir_a = test_dir / 'subdir_a'
            subdir_b = test_dir / 'subdir_b'
            subdir_c = subdir_b / 'subdir_c'

            subdir_a.mkdir(parents=True, exist_ok=True)
            file_a = subdir_a / 'file_a.h'
            file_a.write_text('file_a')

            subdir_c.mkdir(parents=True, exist_ok=True)
            file_c = subdir_c / 'file_c.h'
            file_c.write_text('file_c')

            self.assertEqual(config, license_tools.discover_config(file_a))
            self.assertEqual(config, license_tools.discover_config(file_c))

    def test_multiple_config(self):
        with tempfile.TemporaryDirectory() as test_dir:
            test_dir = Path(test_dir)

            config_root = test_dir / license_tools.LICENSE_JSON
            config_root.write_text("{}")

            subdir_a = test_dir / 'subdir_a'
            subdir_b = test_dir / 'subdir_b'
            subdir_c = subdir_b / 'subdir_c'

            subdir_a.mkdir(parents=True, exist_ok=True)
            file_a = subdir_a / 'file_a.h'
            file_a.write_text('file_a')

            subdir_c.mkdir(parents=True, exist_ok=True)
            file_c = subdir_c / 'file_c.h'
            file_c.write_text('file_c')

            config_c = subdir_c / license_tools.LICENSE_JSON
            config_c.write_text("{}")

            self.assertEqual(config_root, license_tools.discover_config(file_a))
            self.assertEqual(config_c, license_tools.discover_config(file_c))

    def test_multiple_config_subtree(self):
        with tempfile.TemporaryDirectory() as test_dir:
            test_dir = Path(test_dir)

            config_root = test_dir / license_tools.LICENSE_JSON
            config_root.write_text("{}")

            subdir_a = test_dir / 'subdir_a'
            subdir_b = test_dir / 'subdir_b'
            subdir_c = subdir_b / 'subdir_c'

            subdir_a.mkdir(parents=True, exist_ok=True)
            file_a = subdir_a / 'file_a.h'
            file_a.write_text('file_a')

            subdir_c.mkdir(parents=True, exist_ok=True)
            file_c = subdir_c / 'file_c.h'
            file_c.write_text('file_c')

            config_b = subdir_b / license_tools.LICENSE_JSON
            config_b.write_text("{}")

            self.assertEqual(config_root, license_tools.discover_config(file_a))
            self.assertEqual(config_b, license_tools.discover_config(file_c))
