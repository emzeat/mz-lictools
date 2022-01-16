"""
 test.py

 Copyright (c) 2021 - 2022 Marius Zwicker
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

import license_tools
import unittest
import pathlib

BASE = pathlib.Path(__file__).parent


class TestParserCStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-1author_1year.h')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedCStyle-1author_1year.h')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-1author_2years.cxx')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedCStyle-1author_2years.cxx')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-2authors_2years.c')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedCStyle-2authors_2years.c')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)


class TestParserPoundStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserPoundStyle-1author_1year.cmake')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)", parsed.remainder)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedPoundStyle-1author_1year.cmake')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserPoundStyle-1author_2years.sh')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedPoundStyle-1author_2years.sh')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserPoundStyle-2authors_2years')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedPoundStyle-2authors_2years')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)


class TestParserDocStringStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserDocStringStyle-1author_1year.py')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedDocStringStyle-1author_1year.py')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserDocStringStyle-1author_2years.py')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedDocStringStyle-1author_2years.py')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserDocStringStyle-2authors_2years')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedDocStringStyle-2authors_2years')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)


class TestParserXmlStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserXmlStyle-1author_1year.xml')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("<xml />", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserXmlStyle-1author_2years.htm')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    def test_parse_2authors_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserXmlStyle-2authors_2years.html')
        self.assertEqual(3, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2021, parsed.authors[0].year_to)
        self.assertEqual("Awesome Limited Inc.", parsed.authors[1].name)
        self.assertEqual(2012, parsed.authors[1].year_from)
        self.assertEqual(2013, parsed.authors[1].year_to)
        self.assertEqual("My Company", parsed.authors[2].name)
        self.assertEqual(2013, parsed.authors[2].year_from)
        self.assertEqual(2020, parsed.authors[2].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)


class TestHeader(unittest.TestCase):

    def test_generator(self):
        self.maxDiff = None
        author1 = license_tools.Author('Max Muster', 2013, 2020)
        author2 = license_tools.Author('Umbrella Inc', 2021, 2021)
        authors = [author1, author2]

        for l in license_tools.LICENSES:
            license = license_tools.License(l)
            header = license_tools.Header(license)
            filename = f'TestHeader-c_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.C_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise

            filename = f'TestHeader-pound_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.POUND_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise

            filename = f'TestHeader-docstring_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.DOCSTRING_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise

            filename = f'TestHeader-xml_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.XML_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise


class TestTool(unittest.TestCase):

    def test_bump(self):
        self.maxDiff = None
        author = license_tools.Author("Test Guy", year_to=2021)
        license = license_tools.License("Apache-2.0")
        tool = license_tools.Tool(
            default_license=license, default_author=author)
        for file in BASE.glob('test/TestTool-bump*.input.*'):
            stem = file.name.split('.')[0]
            style, result = tool.bump(file, keep_license=True)
            self.assertIsNotNone(result)
            try:
                with open(BASE / 'test' / (stem + ".expected"), 'r') as expected:
                    self.assertEqual(expected.read(), result,
                                     f"{file}, style={style}\n---\n{result}\n---")
            except:
                print(f"{file}, style={style}\n---\n{result}\n---")
                with open(BASE / 'test' / (stem + ".expected"), 'w') as expected:
                    expected.write(result)
                raise


if __name__ == '__main__':
    unittest.main()
