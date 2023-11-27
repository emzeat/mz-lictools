# test.py
#
# Copyright (c) 2021 - 2023 Marius Zwicker
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

from asyncio import subprocess
import functools
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest
import license_tools

BASE = pathlib.Path(__file__).resolve().absolute().parent


# pin the year to 2022 which is the year tests have been
# written to match the output on
os.putenv('LICTOOLS_OVERRIDE_YEAR', '2022')


def _to_unix(input: str):
    return input.replace('\r\n', '\n')


def _to_dos(input: str):
    return _to_unix(input).replace('\n', '\r\n')


def _render_endings(input: str):
    return input.replace('\r', '\\r').replace('\n', '\\n\n')


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

    @parser_test(BASE / 'test/TestParserCStyle-1author_1year.h')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/TestParserTaggedCStyle-1author_1year.h')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/TestParserCStyle-copyright_caps.h')
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

    @parser_test(BASE / 'test/TestParserCStyle-1author_1year.hpp')
    def test_1author_1year_dash(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("AB_CD-Team", parsed.authors[0].name)
        self.assertEqual(1984, parsed.authors[0].year_from)
        self.assertEqual(1984, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("#include <stdio.h>", parsed.remainder)

    @parser_test(BASE / 'test/TestParserCStyle-non_greedy.hpp')
    def test_non_greedy(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2012, parsed.authors[0].year_from)
        self.assertEqual(2018, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "Permission to use"), parsed.license)
        self.assertEqual("#ifndef GEN_NON_", parsed.remainder[:16])

    @parser_test(file=BASE / 'test/TestParserTaggedCStyle-non_greedy.hpp')
    def test_tagged_non_greedy(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2012, parsed.authors[0].year_from)
        self.assertEqual(2018, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "Permission to use"), parsed.license)
        self.assertEqual("#ifndef GEN_NON_", parsed.remainder[:16])

    @parser_test(BASE / 'test/TestParserCStyle-1author_2years.cxx')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserTaggedCStyle-1author_2years.cxx')
    def test_tagged_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserCStyle-2authors_2years.c')
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

    @parser_test(BASE / 'test/TestParserTaggedCStyle-2authors_2years.c')
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

    @parser_test(BASE / 'test/TestParserPoundStyle-1author_1year.cmake')
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

    @parser_test(BASE / 'test/TestParserPoundStyle-no_space.py')
    def test_no_space(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    @parser_test(BASE / 'test/TestParserPoundStyle-no_content.py')
    def test_no_content(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("", parsed.remainder)

    @parser_test(BASE / 'test/TestParserTaggedPoundStyle-1author_1year.cmake')
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

    @parser_test(BASE / 'test/TestParserPoundStyle-1author_2years.sh')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserTaggedPoundStyle-1author_2years.sh')
    def test_tagged_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserPoundStyle-2authors_2years')
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

    @parser_test(BASE / 'test/TestParserTaggedPoundStyle-2authors_2years')
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

    @parser_test(BASE / 'test/TestParserDocStringStyle-1author_1year.py')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    @parser_test(BASE / 'test/TestParserTaggedDocStringStyle-1author_1year.py')
    def test_tagged_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("import unittest", parsed.remainder)

    @parser_test(BASE / 'test/TestParserDocStringStyle-1author_2years.py')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserTaggedDocStringStyle-1author_2years.py')
    def test_tagged_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserDocStringStyle-2authors_2years')
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

    @parser_test(BASE / 'test/TestParserTaggedDocStringStyle-2authors_2years')
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

    @parser_test(BASE / 'test/TestParserXmlStyle-1author_1year.xml')
    def test_1author_1year(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2010, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)
        self.assertEqual("<xml />", parsed.remainder)

    @parser_test(BASE / 'test/TestParserXmlStyle-1author_2years.htm')
    def test_1author_2years(self, parsed):
        self.assertEqual(1, len(parsed.authors))
        self.assertEqual("Max Muster", parsed.authors[0].name)
        self.assertEqual(2010, parsed.authors[0].year_from)
        self.assertEqual(2013, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.XML_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith(
            "This library is"), parsed.license)

    @parser_test(BASE / 'test/TestParserXmlStyle-2authors_2years.html')
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

    @parser_test(BASE / 'test/TestParserXmlStyle-no_license.html')
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

    @parser_test(BASE / 'test/TestParserBatchStyle-1author_1year.bat')
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

    @parser_test(BASE / 'test/TestParserTaggedBatchStyle-1author_1year.bat')
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

    @parser_test(BASE / 'test/TestParserBatchStyle-1author_2years.bat')
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

    @parser_test(BASE / 'test/TestParserTaggedBatchStyle-1author_2years.bat')
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

    @parser_test(BASE / 'test/TestParserSlashStyle-1author_1year.rc')
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

    @parser_test(BASE / 'test/TestParserTaggedSlashStyle-1author_1year.rc')
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

    @parser_test(BASE / 'test/TestParserSlashStyle-multiline_author.rc')
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

    @parser_test(BASE / 'test/TestParserSlashStyle-comment_after_license.c')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('// System'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserDocStringStyle-comment_after_license.py')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('# System'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserPoundStyle-comment_after_license.cmake')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('# rpath handling on OSX'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserSlashStyle-no_newline_after_license.c')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('#include'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserDocStringStyle-no_newline_after_license.py')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('import sys'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserPoundStyle-no_newline_after_license.cmake')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('set(CMAKE_MACOSX_RPATH ON)'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserSlashStyle-no_newline_after_license_extra_slash.c')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.C_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('#include'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserDocStringStyle-no_newline_after_license_extra_pound.py')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DOCSTRING_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('import sys'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserPoundStyle-no_newline_after_license_extra_pound.cmake')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.POUND_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('set(CMAKE_MACOSX_RPATH ON)'), parsed.remainder)


class TestParserDashStyle(unittest.TestCase):

    @parser_test(BASE / 'test/TestParserDashStyle-comment_after_license.lua')
    def test_comment_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DASH_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('-- defines'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserDashStyle-no_newline_after_license.lua')
    def test_no_newline_after_license(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DASH_STYLE, parsed.style)
        self.assertEqual(None, parsed.license)
        self.assertTrue(parsed.remainder.startswith('print'), parsed.remainder)

    @parser_test(BASE / 'test/TestParserDashStyle-no_newline_after_license_extra_dash.lua')
    def test_no_newline_after_license_extra_slash(self, parsed):
        self.assertEqual(1, len(parsed.authors), str(parsed.authors))
        self.assertEqual("Test Author", parsed.authors[0].name)
        self.assertEqual(2022, parsed.authors[0].year_from)
        self.assertEqual(2022, parsed.authors[0].year_to)
        self.assertEqual(license_tools.Style.DASH_STYLE, parsed.style)
        self.assertTrue(parsed.license.startswith('SPDX-License-Identifier:'), parsed.license)
        self.assertTrue(parsed.remainder.startswith('print'), parsed.remainder)


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

            filename = f'TestHeader-dash_{l}.expected'
            output = header.render(
                filename, authors, license_tools.Style.DASH_STYLE)
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
        input = BASE / 'test/TestTool-bump_old_copyright_year.input.cxx'
        expected = BASE / 'test/TestTool-bump_old_copyright_year.expected'
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


for file in BASE.glob('test/TestTool-bump*.input.*'):
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
                with open(BASE / 'test' / (stem + ".expected"), 'r') as expected:
                    self.assertEqual(expected.read(), result)
            except:
                print(f"{file}, style={style}\nACTUAL ---\n{result}\nWANT ---")
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
