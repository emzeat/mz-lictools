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

from asyncio import subprocess
import shutil
import license_tools
import unittest
import pathlib
import tempfile
import subprocess
import os

BASE = pathlib.Path(__file__).resolve().absolute().parent


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
        with self._prepare_repo(BASE / 'test/package_bad_license.patch',
                                BASE / 'test/package_bad_license.patch') as repo:
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_no_config(self):
        with self._prepare_repo(BASE / 'test/package_bad_license.patch',
                                BASE / 'test/package_bad_license.patch') as repo:
            (pathlib.Path(repo) / '.license-tools-config.json').unlink()
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_bad_license(self):
        with self._prepare_repo(BASE / 'test/package_bad_license.patch',
                                BASE / 'test/package_bad_license.json') as repo:
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_force_license(self):
        with self._prepare_repo(BASE / 'test/package_force_license.patch',
                                BASE / 'test/package_force_license.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_force_license.diff')

    def test_retain_license(self):
        with self._prepare_repo(BASE / 'test/package_retain_license.patch',
                                BASE / 'test/package_retain_license.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_retain_license.diff')

    def test_duplicate_authors(self):
        with self._prepare_repo(BASE / 'test/package_duplicate_authors.patch',
                                BASE / 'test/package_duplicate_authors.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_duplicate_authors.diff')

    def test_new_company(self):
        with self._prepare_repo(BASE / 'test/package_new_company.patch',
                                BASE / 'test/package_new_company.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_new_company.diff')

    def test_apply(self):
        with self._prepare_repo(BASE / 'test/package_apply.patch',
                                BASE / 'test/package_apply.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_apply.diff')

    def test_no_changes(self):
        with self._prepare_repo(BASE / 'test/package_no_changes.patch',
                                BASE / 'test/package_no_changes.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_no_changes.diff')

    def test_from_git_apply(self):
        with self._prepare_repo(BASE / 'test/package_from_git_apply.patch',
                                BASE / 'test/package_from_git_apply.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_from_git_apply.diff')

    def test_from_git_no_changes(self):
        with self._prepare_repo(BASE / 'test/package_from_git_no_changes.patch',
                                BASE / 'test/package_from_git_no_changes.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_from_git_no_changes.diff')

    def test_from_git_no_repo(self):
        with self._prepare_repo(BASE / 'test/package_from_git_no_repo.patch',
                                BASE / 'test/package_from_git_no_repo.json') as repo:
            shutil.rmtree(pathlib.Path(repo) / '.git')
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_new_author(self):
        with self._prepare_repo(BASE / 'test/package_from_git_new_author.patch',
                                BASE / 'test/package_from_git_new_author.json') as repo:
            code = pathlib.Path(repo) / 'code.cpp'
            code.write_text(code.read_text() + "\ninline void unused(){}\n\n")
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_from_git_new_author.diff')

    def test_author_alias(self):
        with self._prepare_repo(BASE / 'test/package_author_alias.patch',
                                BASE / 'test/package_author_alias.json') as repo:
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package_author_alias.diff')


if __name__ == '__main__':
    unittest.main()
