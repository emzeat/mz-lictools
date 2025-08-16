# test.py
#
# Copyright (c) 2021 - 2024 Marius Zwicker
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
import license_tools


class TestFileFilter(unittest.TestCase):

    def test_recursive_includes(self):
        EXPRESSIONS = [
            ('foo.txt', ['*']),
            ('foo.txt', ['*.txt']),
            ('asterisk?.txt', ['asterisk[?].txt']),
            ('asterisk.txt', ['asterisk.txt']),
            ('asteris!.txt', ['asteris!.txt']),
            ('/foo.txt', ['/*.txt']),
            ('foo.txt', ['**********.txt']),
            ('foo.txt', ['**/*']),
            ('bla/foo.txt', ['*/*.txt']),
            ('bla/foo.txt', ['**/*.txt']),
            ('bla/da/foo.txt', ['**/*.txt']),
            ('bla/da/foo.txt', ['**/*[t]']),
            ('bla/da/foo.txt', ['**/*']),
            ('bla/da/foo.txt', ['bla/**/*']),
            ('bla/da/d1u/foo.txt', ['bla/**/*']),
            ('bla/da/foo.txt', ['**/*.txt']),
            ('da_foo.txt', ['[de]a_foo.txt']),
            ('da_foo.txt', ['da_foo.t?t']),
        ]
        for file_rel, includes in EXPRESSIONS:
            try:
                self.assertTrue(license_tools.FileFilter.is_included(file_rel, includes, []))
            except:
                print(f"file_rel={file_rel} includes={includes}")
                raise
        EXPRESSIONS = [
            ('foo/foo.txt', ['*']),
            ('asteriskk.txt', ['asterisk[?].txt']),
            ('foo/foo.txt', ['**.txt']),
            ('bla/foo.doc', ['*/*.txt']),
            ('bla/da/foo.txt', ['*/*.txt']),
            ('da_foo.txt', ['[!de]a_foo.txt']),
            ('da_foo.txt', ['?.txt']),
            ('bla/da/foo_txt', ['**/*.txt']),
        ]
        for file_rel, includes in EXPRESSIONS:
            try:
                self.assertFalse(license_tools.FileFilter.is_included(file_rel, includes, []))
            except:
                print(f"file_rel={file_rel} includes={includes}")
                raise
