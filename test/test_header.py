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
import unittest
import license_tools

BASE = pathlib.Path(__file__).resolve().absolute().parent.parent


class TestHeader(unittest.TestCase):

    def test_generator(self):
        self.maxDiff = None
        author1 = license_tools.Author('Max Muster', 2013, 2020)
        author2 = license_tools.Author('Umbrella Inc', 2021, 2021)
        authors = [author1, author2]

        for l in license_tools.LICENSES:
            license = license_tools.License(builtin=l)
            header = license_tools.Header(license)

            for style in license_tools.Style:
                if license_tools.Style.UNKNOWN == style:
                    continue
                candidates = {
                    license_tools.Style.C_STYLE: f'TestHeader-c_{l}.expected',
                    license_tools.Style.POUND_STYLE: f'TestHeader-pound_{l}.expected',
                    license_tools.Style.DOCSTRING_STYLE: f'TestHeader-docstring_{l}.expected',
                    license_tools.Style.XML_STYLE: f'TestHeader-xml_{l}.expected',
                    license_tools.Style.BATCH_STYLE: f'TestHeader-batch_{l}.expected',
                    license_tools.Style.SLASH_STYLE: f'TestHeader-slash_{l}.expected',
                    license_tools.Style.DASH_STYLE: f'TestHeader-dash_{l}.expected',
                    license_tools.Style.TRIPLE_SLASH_STYLE: f'TestHeader-triple_slash_{l}.expected',
                    license_tools.Style.GO_TEXT_TEMPLATE_STYLE: f'TestHeader-go_text_template_{l}.expected',
                }
                filename = candidates[style]
                output = header.render(
                    filename, authors, style)
                try:
                    with open(BASE / 'test/generation' / filename, 'r') as expected:
                        self.assertEqual(expected.read(), output)
                    parsed = license_tools.ParsedHeader(
                        contents=output, file=filename)
                    self.assertListEqual(authors, parsed.authors)
                except:
                    with open(BASE / 'test/generation' / filename, 'w') as expected:
                        expected.write(output)
                    raise

            filename = f'TestHeader-no_license_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.C_STYLE)
            try:
                with open(BASE / 'test/generation' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
                parsed = license_tools.ParsedHeader(
                    contents=output, file=filename)
                self.assertListEqual(authors, parsed.authors)
            except:
                with open(BASE / 'test/generation' / filename, 'w') as expected:
                    expected.write(output)
                raise

            header = license_tools.Header(None)
            filename = f'TestHeader-title_{l}.expected'
            output = header.render(
                'My Project', authors, license_tools.Style.C_STYLE)
            try:
                with open(BASE / 'test/generation' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
                parsed = license_tools.ParsedHeader(
                    contents=output, file=filename)
                self.assertListEqual(authors, parsed.authors)
            except:
                with open(BASE / 'test/generation' / filename, 'w') as expected:
                    expected.write(output)
                raise

        custom_license = """
Lorem Bin Title.

Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """
        license = license_tools.License(custom=custom_license)
        header = license_tools.Header(license)
        filename = f'TestHeader-c_custom.expected'
        output = header.render(
            filename, authors, license_tools.Style.C_STYLE)
        try:
            with open(BASE / 'test/generation' / filename, 'r') as expected:
                self.assertEqual(expected.read(), output)
        except:
            with open(BASE / 'test/generation' / filename, 'w') as expected:
                expected.write(output)
            raise
