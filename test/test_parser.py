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

import functools
import pathlib
import unittest
import license_tools

BASE = pathlib.Path(__file__).resolve().absolute().parent.parent


def _to_unix(input: str):
    return input.replace('\r\n', '\n')


def _to_dos(input: str):
    return _to_unix(input).replace('\n', '\r\n')


def _render_endings(input: str):
    return input.replace('\r', '\\r').replace('\n', '\\n\n')


def parser_test(file: pathlib.Path):
    def file_wrapper(func):
        @functools.wraps(func)
        def wrapper(self):
            # make sure any kind of line endings can be parsed
            for contents in (_to_dos(file.read_text()), _to_unix(file.read_text())):
                parsed = license_tools.ParsedHeader(
                    contents=contents, file=file)
                try:
                    func(self, parsed)
                except:
                    print(f"While trying to parse: {file}\n---\n{_render_endings(contents)}\n---\n")
                    raise
        return wrapper
    return file_wrapper


class TestParserCStyle(unittest.TestCase):

    @parser_test(BASE / 'test/parser/TestParserCStyle-1author_1year.h')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserTaggedCStyle-1author_1year.h')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserCStyle-copyright_caps.h')
    def test_copyright_caps(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserCStyle-1author_1year.hpp')
    def test_1author_1year_dash(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("AB_CD-Team", parsed.authors[0].name)
        self.assertEqual(1984, parsed.authors[0].year_from)
        self.assertEqual(1984, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserCStyle-non_greedy.hpp')
    def test_non_greedy(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2012, parsed.authors[0].year_from)
        self.assertEqual(2018, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "Permission to use"), parsed.license)
        self.assertEqual("#ifndef GEN_NON_", parsed.remainder[:16])

    @parser_test(file=BASE / 'test/parser/TestParserTaggedCStyle-non_greedy.hpp')
    def test_tagged_non_greedy(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2012, parsed.authors[0].year_from)
        self.assertEqual(2018, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "Permission to use"), parsed.license)
        self.assertEqual("#ifndef GEN_NON_", parsed.remainder[:16])

    @parser_test(BASE / 'test/parser/TestParserCStyle-1author_2years.cxx')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserTaggedCStyle-1author_2years.cxx')
    def test_tagged_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserCStyle-2authors_2years.c')
    def test_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserTaggedCStyle-2authors_2years.c')
    def test_tagged_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-no_newline_after_license_extra_pound.cmake')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('set(CMAKE_MACOSX_RPATH ON)'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-no_newline_after_license.cmake')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('set(CMAKE_MACOSX_RPATH ON)'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-1author_1year.cmake')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-comment_after_license.cmake')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('# rpath handling on OSX'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-no_space.py')
    def test_no_space(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-no_content.py')
    def test_no_content(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserTaggedPoundStyle-1author_1year.cmake')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-1author_2years.sh')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserTaggedPoundStyle-1author_2years.sh')
    def test_tagged_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserPoundStyle-2authors_2years')
    def test_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserTaggedPoundStyle-2authors_2years')
    def test_tagged_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserDocStringStyle-no_newline_after_license_extra_pound.py')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('import sys'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserDocStringStyle-no_newline_after_license.py')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('import sys'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserDocStringStyle-1author_1year.py')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserTaggedDocStringStyle-1author_1year.py')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserDocStringStyle-1author_2years.py')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserTaggedDocStringStyle-1author_2years.py')
    def test_tagged_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserDocStringStyle-comment_after_license.py')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('# System'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserDocStringStyle-2authors_2years')
    def test_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserTaggedDocStringStyle-2authors_2years')
    def test_tagged_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserXmlStyle-1author_1year.xml')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("<xml />", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserXmlStyle-unicode_marker.xml')
    def test_unicode_marker(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2020, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertListEqual(['\uFEFF', '<?xml version="1.0" encoding="utf-8"?>'], parsed.decls)
        if '\r' in parsed.remainder:
            self.assertEqual("<rcc>\r\n    <!-- qrc sample -->\r\n    <qresource", parsed.remainder[:46])
        else:
            self.assertEqual("<rcc>\n    <!-- qrc sample -->\n    <qresource", parsed.remainder[:44])
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserXmlStyle-1author_2years.htm')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/parser/TestParserXmlStyle-2authors_2years.html')
    def test_2authors_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserXmlStyle-no_license.html')
    def test_no_license(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserBatchStyle-1author_1year.bat')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserTaggedBatchStyle-1author_1year.bat')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserBatchStyle-1author_2years.bat')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.BATCH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "echo.Hello World", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserTaggedBatchStyle-1author_2years.bat')
    def test_tagged_1author_2years(self, parsed):
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

    @parser_test(BASE / 'test/parser/TestParserSlashStyle-1author_1year.rc')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.SLASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserTaggedSlashStyle-1author_1year.rc')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.SLASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserSlashStyle-multiline_author.rc')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Office of code", parsed.authors[0].name)
        self.assertEqual(2003, parsed.authors[0].year_from)
        self.assertEqual(2023, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.SLASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual(
            "#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserSlashStyle-comment_after_license.c')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('// System'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserSlashStyle-brief_spdx.c')
    def test_brief_spdx(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertEqual("SPDX-License-Identifier: Apache-2.0", parsed.license)
        self.assertTrue(parsed.remainder.startswith('// System'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserSlashStyle-no_newline_after_license.c')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('#include'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserSlashStyle-no_newline_after_license_extra_slash.c')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('#include'), parsed.remainder)


class TestParserDashStyle(unittest.TestCase):

    @parser_test(BASE / 'test/parser/TestParserDashStyle-comment_after_license.lua')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DASH_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('-- defines'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserDashStyle-no_newline_after_license.lua')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DASH_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('print'), parsed.remainder)

    @parser_test(BASE / 'test/parser/TestParserDashStyle-no_newline_after_license_extra_dash.lua')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('print'), parsed.remainder)
