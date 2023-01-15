"""
 test.py

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

from asyncio import subprocess
import shutil
import license_tools
import unittest
import pathlib
import tempfile
import subprocess
import os

BASE = pathlib.Path(__file__).resolve().absolute().parent


# pin the year to 2022 which is the year tests have been
# written to match the output on
os.putenv('LICTOOLS_OVERRIDE_YEAR', '2022')


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

    def test_parse_copyright_caps(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-copyright_caps.h')
        self.assertEqual(2, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual("Dana Dot", parsed.authors[1].name)
        self.assertEqual(2011, parsed.authors[1].year_from)
        self.assertEqual(2011, parsed.authors[1].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    def test_parse_1author_1year_dash(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-1author_1year.hpp')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("AB_CD-Team", parsed.authors[0].name)
        self.assertEqual(1984, parsed.authors[0].year_from)
        self.assertEqual(1984, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    def test_parse_non_greedy(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserCStyle-non_greedy.hpp')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2012, parsed.authors[0].year_from)
        self.assertEqual(2018, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "Permission to use"), parsed.license)
        self.assertEqual("#ifndef GEN_NON_", parsed.remainder[:16])

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedCStyle-non_greedy.hpp')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2012, parsed.authors[0].year_from)
        self.assertEqual(2018, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "Permission to use"), parsed.license)
        self.assertEqual("#ifndef GEN_NON_", parsed.remainder[:16])

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

    def test_parse_no_license(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserXmlStyle-no_license.html')
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
        self.assertEqual(None, parsed.license)


class TestParserBatchStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserBatchStyle-1author_1year.bat')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedBatchStyle-1author_1year.bat')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)

    def test_parse_1author_2years(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserBatchStyle-1author_2years.bat')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedBatchStyle-1author_2years.bat')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)


class TestParserSlashStyle(unittest.TestCase):

    def test_parse_1author_1year(self):
        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserSlashStyle-1author_1year.rc')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.SLASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "#include <stdio.h>", parsed.remainder)

        parsed = license_tools.ParsedHeader(
            file=BASE / 'test/TestParserTaggedSlashStyle-1author_1year.rc')
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.SLASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "#include <stdio.h>", parsed.remainder)


class TestHeader(unittest.TestCase):

    def test_generator(self):
        self.maxDiff = None
        author1 = license_tools.Author('Max Muster', 2013, 2020)
        author2 = license_tools.Author('Umbrella Inc', 2021, 2021)
        authors = [author1, author2]

        for l in license_tools.LICENSES:
            license = license_tools.License(builtin=l)
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

            filename = f'TestHeader-batch_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.BATCH_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise

            filename = f'TestHeader-slash_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.SLASH_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise

            header = license_tools.Header(None)
            filename = f'TestHeader-no_license_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.C_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
                    expected.write(output)
                raise

            header = license_tools.Header(None)
            filename = f'TestHeader-title_{l}.expected'
            output = header.render(
                'My Project', authors, license_tools.Style.C_STYLE)
            try:
                with open(BASE / 'test' / filename, 'r') as expected:
                    self.assertEqual(expected.read(), output)
            except:
                with open(BASE / 'test' / filename, 'w') as expected:
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
            with open(BASE / 'test' / filename, 'r') as expected:
                self.assertEqual(expected.read(), output)
        except:
            with open(BASE / 'test' / filename, 'w') as expected:
                expected.write(output)
            raise


class TestTool(unittest.TestCase):
    pass


for file in BASE.glob('test/TestTool-bump*.input.*'):
    author = license_tools.Author("Test Guy", year_to=2021)
    license = license_tools.License("Apache-2.0")
    tool = license_tools.Tool(
        default_license=license, default_author=author)
    name = file.name.split('.')[0]

    def create_test_case():
        input = file
        stem = name

        def test_bump(self):
            style, result = tool.bump(input, keep_license=True)
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
        return test_bump
    setattr(TestTool, f'test_{name.replace("TestTool-","")}', create_test_case())


class TestPackage(unittest.TestCase):

    def _prepare_repo(self, commit: pathlib.Path, config: pathlib.Path):
        # override any external input to the git config so we truly
        # use our expected config to ensure tests cannot fail
        os.putenv('GIT_CONFIG_COUNT', '0')

        wkdir = tempfile.TemporaryDirectory(suffix='lictools')
        try:
            cwd = pathlib.Path(wkdir.name)
            subprocess.check_call('git init --initial-branch=master', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            (cwd / ".gitignore").write_text("")
            subprocess.check_call('git add .gitignore', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('git commit -a -m "Prepare Repo"', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('git config --local user.name "Lictools Unittest"',
                                  cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('git config --local user.email "lictools@unittest.local"',
                                  cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call(f'git am {commit}', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            (cwd / '.license-tools-config.json').write_text(config.read_text())
            return wkdir
        except:
            wkdir.cleanup()
            raise

    def _diff_repo(self, repo: pathlib.Path, expected: pathlib.Path):
        diff = subprocess.check_output('git diff', cwd=repo, shell=True, encoding='utf-8')
        try:
            with open(expected, 'r') as raw:
                self.assertEqual(raw.read(), diff)
        except:
            with open(expected, 'w') as raw:
                raw.write(diff)
            raise

    def test_bad_config(self):
        with self._prepare_repo(BASE / 'test/noglob_package_bad_license.patch',
                                BASE / 'test/noglob_package_bad_license.patch') as repo:
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_no_config(self):
        with self._prepare_repo(BASE / 'test/noglob_package_bad_license.patch',
                                BASE / 'test/noglob_package_bad_license.patch') as repo:
            (pathlib.Path(repo) / '.license-tools-config.json').unlink()
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_bad_license(self):
        with self._prepare_repo(BASE / 'test/noglob_package_bad_license.patch',
                                BASE / 'test/noglob_package_bad_license.json') as repo:
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_from_git_no_repo(self):
        with self._prepare_repo(BASE / 'test/noglob_package_from_git_no_repo.patch',
                                BASE / 'test/noglob_package_from_git_no_repo.json') as repo:
            shutil.rmtree(pathlib.Path(repo) / '.git')
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_new_author(self):
        with self._prepare_repo(BASE / 'test/noglob_package_from_git_new_author.patch',
                                BASE / 'test/noglob_package_from_git_new_author.json') as repo:
            code = pathlib.Path(repo) / 'code.cpp'
            code.write_text(code.read_text() + "\ninline void unused(){}\n\n")
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/noglob_package_from_git_new_author.diff')


for file in BASE.glob('test/package_*.patch'):
    def create_test_case():
        patch = file
        json = patch.with_suffix('.json')
        diff = patch.with_suffix('.diff')

        def test_glob_case(self):
            with self._prepare_repo(patch, json) as repo:
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)
                self._diff_repo(repo, diff)
        return test_glob_case
    setattr(TestPackage, f'test_{file.stem.replace("package_", "")}', create_test_case())


if __name__ == '__main__':
    unittest.main()
