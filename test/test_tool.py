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

import pathlib
import tempfile
import unittest
import license_tools

BASE = pathlib.Path(__file__).resolve().absolute().parent.parent


class TestTool(unittest.TestCase):

    def _to_unix(self, input: str):
        return input.replace('\r\n', '\n')

    def _to_dos(self, input: str):
        return self._to_unix(input).replace('\n', '\r\n')

    def _render_endings(self, input: str):
        return input.replace('\r', '\\r').replace('\n', '\\n\n')

    def test_retain_newline(self):
        author = license_tools.Author("Test Guy", year_to=2021)
        license = license_tools.License("Apache-2.0")
        title = license_tools.Title("filename")
        tool = license_tools.Tool(
            default_license=license, default_author=author)
        input = BASE / 'test/tool/TestTool-bump_old_copyright_year.input.cxx'
        expected = BASE / 'test/tool/TestTool-bump_old_copyright_year.expected'
        with tempfile.TemporaryDirectory() as wkdir:
            dut = pathlib.Path(wkdir) / input.name
            # verify unix line endings get retained
            input_unix = self._to_unix(input.read_text())
            expected_unix = self._to_unix(expected.read_text())
            with open(dut, mode='w', newline='', encoding='utf8') as dut_io:
                dut_io.write(input_unix)
            _, result = tool.bump(dut, keep_license=True, title=title)
            self.assertEqual(expected_unix, result,
                             f"\nACTUAL ---\n{self._render_endings(result)}\nWANT ---\n{self._render_endings(expected_unix)}\n---")
            # verify dos line endings get retained
            input_dos = self._to_dos(input.read_text())
            expected_dos = self._to_dos(expected.read_text())
            with open(dut, mode='w', newline='', encoding='utf8') as dut_io:
                dut_io.write(input_dos)
            _, result = tool.bump(dut, keep_license=True, title=title)
            self.assertEqual(expected_dos, result,
                             f"\nACTUAL ---\n{self._render_endings(result)}\nWANT ---\n{self._render_endings(expected_dos)}\n---")


for file in BASE.glob('test/tool/TestTool-bump*.input.*'):
    author = license_tools.Author("Test Guy", year_to=2021)
    license = license_tools.License("Apache-2.0")
    title = license_tools.Title("filename")
    tool = license_tools.Tool(
        default_license=license, default_author=author)
    name = file.name.split('.')[0]

    def create_test_case():
        input = file
        stem = name

        def test_bump(self):
            style, result = tool.bump(input, title=title, keep_license=True)
            self.assertIsNotNone(result)
            try:
                with open(BASE / 'test/tool' / (stem + ".expected"), 'r') as expected:
                    self.assertEqual(expected.read(), result)
            except:
                print(f"{file}, style={style}\nACTUAL ---\n{result}\nWANT ---")
                with open(BASE / 'test/tool' / (stem + ".expected"), 'w') as expected:
                    expected.write(result)
                raise
        return test_bump
    setattr(TestTool, f'test_{name.replace("TestTool-","")}', create_test_case())
