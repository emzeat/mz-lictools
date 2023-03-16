#
# __init__.py
#
# Copyright (c) 2012 - 2023 Marius Zwicker
# All rights reserved.
#
# SPDX-License-Identifier: GPL-2.0-or-later
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

"""
See README.md for detail and documentation
"""

import argparse
import datetime
import enum
import functools
import json
import logging
import os
import pathlib
import re
import subprocess
import sys
from collections import namedtuple
from copy import copy
from operator import attrgetter
from typing import Dict
import jinja2

BASE_DIR = pathlib.Path(__file__).parent
CW_DIR = pathlib.Path.cwd()
SPDX_LICENSES = list(BASE_DIR.glob('*.spdx'))
OTHER_LICENSES = list(BASE_DIR.glob('*.license'))
LICENSES = {license_file.stem: license_file for license_file in SPDX_LICENSES + OTHER_LICENSES}
LICENSE_JSON = '.license-tools-config.json'


class DateUtils:
    """Utilities for date functions used in this package"""
    _current_year = None

    @staticmethod
    def current_year():
        """
        Returns the current year

        Override using the LICTOOLS_OVERRIDE_YEAR env variable
        """
        if DateUtils._current_year is None:
            year = os.getenv('LICTOOLS_OVERRIDE_YEAR', datetime.date.today().year)
            DateUtils._current_year = int(year)
        return DateUtils._current_year


class Style(enum.Enum):
    """Enumerates the different known comment styles"""
    UNKNOWN = 1
    C_STYLE = 2
    POUND_STYLE = 3
    DOCSTRING_STYLE = 4
    XML_STYLE = 5
    BATCH_STYLE = 6
    SLASH_STYLE = 7

    @staticmethod
    def from_suffix(ext):
        """Tries to determine the style based on a file suffix"""
        mapping = {
            '.cc': Style.C_STYLE,
            '.cxx': Style.C_STYLE,
            '.cpp': Style.C_STYLE,
            '.c': Style.C_STYLE,
            '.hpp': Style.C_STYLE,
            '.h': Style.C_STYLE,
            '.hxx': Style.C_STYLE,
            '.mm': Style.C_STYLE,
            '.m': Style.C_STYLE,
            '.qml': Style.C_STYLE,
            '.java': Style.C_STYLE,
            '.glsl': Style.C_STYLE,
            '.frag': Style.C_STYLE,
            '.vert': Style.C_STYLE,
            '.rb': Style.POUND_STYLE,
            '.py': Style.DOCSTRING_STYLE,
            '.sh': Style.POUND_STYLE,
            '.bash': Style.POUND_STYLE,
            '.command': Style.POUND_STYLE,
            '.cmake': Style.POUND_STYLE,
            '.xml': Style.XML_STYLE,
            '.htm': Style.XML_STYLE,
            '.html': Style.XML_STYLE,
            '.ui': Style.XML_STYLE,
            '.qrc': Style.XML_STYLE,
            '.svg': Style.XML_STYLE,
            '.bat': Style.BATCH_STYLE,
            '.rc': Style.SLASH_STYLE,
            '.yml': Style.POUND_STYLE,
            '.yaml': Style.POUND_STYLE,
        }
        return mapping.get(ext, Style.UNKNOWN)

    @staticmethod
    def from_name(name):
        """Tries to determine the style based on a file name"""
        mapping = {
            'CMakeLists.txt': Style.POUND_STYLE,
            'requirements.txt': Style.POUND_STYLE
        }
        return mapping.get(name, Style.UNKNOWN)

    @staticmethod
    def patterns(style=None):
        """
        Returns a list of regex and style pairs

        Each regex has two match groups, one for the license and one for the remainder

        :style: Use to limit the list of patterns to the given style
        """
        style_patterns = [
            (Style.C_STYLE,
                r"/\*(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)\* +@LICENSE_HEADER_END@(?:.*?)\*/(?P<body>.*)"),
            (Style.C_STYLE,
                r"/\*(?P<authors>.+?)@MLBA_OPEN_LICENSE_HEADER_START@(?P<license>.+?)\* +@MLBA_OPEN_LICENSE_HEADER_END@(?:.*?)\*/(?P<body>.*)"),
            (Style.C_STYLE,
                r"/\*(?P<authors>.+?)All rights reserved\.(?P<license>.+?)\*/(?P<body>.*)"),
            (Style.POUND_STYLE,
                r"#(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)# +@LICENSE_HEADER_END@(?:.*?)#\r?\n(?P<body>.*)"),
            (Style.POUND_STYLE,
                r"#(?P<authors>.+?)All rights reserved\.(?P<license>.+?)#\r?\n[^#](?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"\"\"\"\r?\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\r?\n\"\"\"(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"\"\"\"\r?\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)\"\"\"\r?\n(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"#(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)# +@LICENSE_HEADER_END@(?:.*?)#\r?\n(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"#(?P<authors>.+?)All rights reserved\.(?P<license>.+?)#\r?\n[^#](?P<body>.*)"),
            (Style.XML_STYLE,
                r"<!--\r?\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\r?\n-->(?P<body>.*)"),
            (Style.XML_STYLE,
                r"<!--\r?\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)-->\r?\n(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"REM(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)REM\r?\n(?!REM)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"REM(?P<authors>.+?)All rights reserved\.(?P<license>.+?)REM\r?\n(?!REM)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"::(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)::\r?\n(?!::)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"::(?P<authors>.+?)All rights reserved\.(?P<license>.+?)::\r?\n(?!::)(?P<body>.*)"),
            (Style.SLASH_STYLE,
                r"//(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)// +@LICENSE_HEADER_END@(?:.*?)//\r?\n(?P<body>.*)"),
            (Style.SLASH_STYLE,
                r"//(?P<authors>.+?)All rights reserved\.(?P<license>.+?)//\r?\n[^//](?P<body>.*)"),
            (Style.UNKNOWN,
                r"(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?P<body>.*)"),
        ]
        if style is None:
            style = Style.UNKNOWN
        if style == Style.UNKNOWN:
            # slow path, we have to try all of the patterns
            return style_patterns
        # fast path, we can reduce the number of patterns
        return [(s, p) for s, p in style_patterns if s == style]  # pylint: disable=invalid-name

    @staticmethod
    def declarations():
        """
        Returns a list of document declarations retained at the first line

        Each entry is a pair of matching regex and additional flags required
        """
        return [
            # something like '#!/usr/bin/env bash'
            (r'^#!.+', 0),
            # something like '# -*- coding: utf-8 -*-'
            (r'^# -\*-.+', 0),
            # something like '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
            # note: use xmllint to easily validate generated output
            (r'^<\?xml .+?\?>', 0),
            # something like '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
            (r'^<!DOCTYPE .+?>', 0),
            # beginning of batch files silencing output but only if the very first line
            (r'^@echo off', 0)
        ]

    @staticmethod
    def decorators(style):
        """
        Returns the decorator descriptions for a given style

        Expect a named tuple with entries for start, prefix, end
        as well as a pattern to strip these decorators from a line
        """
        Decorator = namedtuple('Decorator', 'start prefix end pattern')
        if style == Style.C_STYLE:
            return Decorator('/*', ' *', ' */', r' ?(?:\*) ?')
        if style == Style.POUND_STYLE:
            return Decorator('#', '#', '#', r' ?(?:#) ?')
        if style == Style.DOCSTRING_STYLE:
            # the pattern will help to translate any #-style and """-style docstrings
            return Decorator('#', '#', '#', r' ?(?:#) ?')
        if style == Style.XML_STYLE:
            return Decorator('<!--', '', '-->', None)
        if style == Style.BATCH_STYLE:
            return Decorator('REM', 'REM', 'REM', r' ?(?:REM|::) ?')
        if style == Style.SLASH_STYLE:
            return Decorator('//', '//', '//', r' ?(?://) ?')
        return Decorator('', '', '', None)


class Author:
    """Describes an author of a file"""

    def __init__(self, name: str, year_from: int = None,
                 year_to: int = None,
                 git_repo=None):
        """
        Creates a new author
        :name: The name of the author
        :year_from: The first year the author contributed. Will default
                  to year_to when omitted.
        :year_to: The last year the author contributed. Will default
                  to DateUtils.CURRENT_YEAR when omitted.
        """
        self.name = name
        self.git_repo = git_repo
        self.name_from_git = git_repo is not None
        if year_to is None:
            year_to = DateUtils.current_year()
        self.year_to = year_to
        if year_from:
            self.year_from = year_from
        else:
            self.year_from = year_to


class GitRepo:
    """Git repository object"""

    @staticmethod
    @functools.lru_cache(maxsize=256, typed=True)
    def find_git_root(cwd: pathlib.Path) -> pathlib.Path:
        """Tries to find the git root as seen from cwd"""
        root = subprocess.check_output(
            'git rev-parse --show-toplevel', cwd=cwd, stderr=subprocess.STDOUT, shell=True, encoding='utf-8')
        return pathlib.Path(root.strip())

    @staticmethod
    @functools.lru_cache(maxsize=256, typed=True)
    def author_name_from_config(cwd: pathlib.Path) -> str:
        """Returns the author name as set via gitconfig and seen from cwd"""
        git_author = subprocess.check_output(
            'git config user.name', cwd=cwd, stderr=subprocess.STDOUT, shell=True, encoding='utf-8')
        return git_author.strip()

    def __init__(self, cwd=None):
        """
        Creates a repository object using the current working dir to determine the root

        :cwd: Directory to create the repo obj from, leave None to use current wkdir
        :throws RuntimeError: When failing to detect the root
        """
        try:
            if cwd is None:
                cwd = CW_DIR
            self.git_root = GitRepo.find_git_root(cwd)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"Not a git repo: {error.output}") from error

    def author_from_config(self) -> Author:
        """Returns the author as set via gitconfig"""
        try:
            return Author(name=GitRepo.author_name_from_config(self.git_root), git_repo=self)
        except subprocess.CalledProcessError as error:
            logging.fatal(f"Failed to fetch author using git: {error.output}")
            return None

    def author_from_history(self, filename: pathlib.Path) -> Author:
        """Returns the author who touched the file for the last time or None"""
        file_rel = filename.relative_to(self.git_root)
        try:
            author_raw = subprocess.check_output(
                f'git log -1 --date=format:%Y --pretty=format:"%an\t%ad" -- {file_rel}',
                cwd=self.git_root, stderr=subprocess.STDOUT, shell=True,
                encoding='utf-8')
            author_raw = author_raw.strip()
            author_name, author_year = author_raw.split('\t')
            author_year = int(author_year)
            logging.debug(f"{file_rel} was last touched by \"{author_name}\" during {author_year}")
            return Author(name=author_name, year_to=author_year, git_repo=self)
        except ValueError:
            pass
        except subprocess.CalledProcessError:
            pass
        return None

    def is_modified_in_tree(self, filename: pathlib.Path) -> bool:
        """Returns true when the file has uncommited chnages in the tree"""
        file_rel = filename.relative_to(self.git_root)
        try:
            diff = subprocess.check_output(
                f'git diff --name-only HEAD -- {file_rel}',
                cwd=self.git_root, stderr=subprocess.STDOUT, shell=True,
                encoding='utf-8').strip()
            if len(diff) != 0:
                logging.debug(f"{file_rel} was just modified: {diff}")
                return True
        except subprocess.CalledProcessError:
            pass
        return False


class License:
    """Describes a license to be added to a header"""

    def __init__(self, builtin: str = None, custom: str = None):
        """
        Creates a new license

        Either builtin or custom need to be specified.

        :builtin: One of the supported licenses, see LICENSES
        :custom: Configures a custom license text
        """
        if builtin:
            self.name = builtin
            self.header = LICENSES.get(builtin, None)
            if self.header is None:
                raise TypeError(f"No such license '{builtin}'")
            self.builtin = True
            self.spdx = self.header in SPDX_LICENSES
            self.header = self.header.name
        elif custom:
            self.name = 'custom'
            self.header = custom
            self.builtin = False
            self.spdx = False
        else:
            raise KeyError("Need to select a 'builtin' or provide 'custom' license")


class Header:
    """Describes a header to be rendered with license and authors"""

    def __init__(self, default_license):
        """Creates a new header using given default license"""
        loader = jinja2.FileSystemLoader(BASE_DIR)
        self.env = jinja2.Environment(loader=loader)
        self.template = self.env.get_template('Header.j2')
        self.default_license = default_license

    def render(self, title: str, authors, style: Style, company: str = None, license: str = None) -> str:
        """
        Renders a header to a string
        :title: The title to put at the top of the file, usually the filename
        :authors: A list of authors which contributed to the file
        :style: The comment style to use when generating the header
        :company: An optional company string to be included
        :license: An optional license string to be used, if omitted the default_license will apply
        """
        if company is None:
            company = 'the authors'
        header = self.template.render(default_license=self.default_license,
                                      license=license, title=title, authors=authors, company=company)
        decorators = Style.decorators(style)
        header = header.split('\n')
        header = [decorators.start] + \
                 [f'{decorators.prefix} ' + h if h.strip() else decorators.prefix for h in header] + [decorators.end, '']
        return '\n'.join(header)


class ParsedHeader:
    """A license header parsed from an existing file"""

    def __init__(self, file: pathlib.PurePath = None, contents: str = None):
        """
        Parses a header from the given file

        :file: The filepath of the header
        :contenst: The contents of the header, if None this will be read from file
        """
        if contents is None:
            with open(file, 'r', encoding='utf-8', newline='') as file_obj:
                contents = file_obj.read()
        # style is determined from the extension, if unknown we try a second attempt using the contents below
        self.style = Style.from_suffix(file.suffix)
        if self.style == Style.UNKNOWN:
            self.style = Style.from_name(file.name)
        # strip but remember any shebang, encoding or doctype at the beginning
        self.decls = []

        def extract_decl(pattern, contents, flags=re.MULTILINE):
            decl = re.match(pattern, contents, flags)
            if decl:
                decl = decl[0]
                self.decls.append(decl)
                # remove the decl including the newline
                return contents[len(decl):].lstrip()
            return contents
        for decl, flags in Style.declarations():
            contents = extract_decl(decl, contents, flags)
        # any known license is wrapped in well-known tags
        for style, pattern in Style.patterns(self.style):
            match = re.match(pattern, contents, re.MULTILINE | re.DOTALL)
            if match:
                if style != Style.UNKNOWN:
                    self.style = style
                break
        if match:
            # grab the matched license but remove any # or * per line prefix decorators
            self.license = match.group('license')
            decorators = Style.decorators(self.style)
            if decorators.pattern:
                self.license = re.sub(decorators.pattern, '', self.license, flags=re.MULTILINE)
            self.license = self.license.strip('\n\r')
            if self.license.startswith(' '):
                # filter any leading indends
                self.license = self.license.replace('\n ', '\n')
            self.license = self.license.strip()
            if self.license == "":
                # When license is an empty string reset to None
                self.license = None
            self.remainder = match.group('body').strip()
        else:
            self.license = None
            self.remainder = contents.strip()
        # determine the line endings from the remainder or default to platform if none
        if self.remainder:
            if '\r\n' in self.remainder:
                self.newline = '\r\n'
            else:
                self.newline = '\n'
        else:
            self.newline = os.linesep
        # in case we have a matched header we can use its authors group to limit our search
        # use a regex to extract existing authors, i.e. any line starting with 'Copyright'
        if match:
            authors_raw = match.group('authors') or contents
        else:
            authors_raw = contents
        self.authors = []
        for match in re.finditer(r" Copyright[^\d]*(?P<from>[0-9]+) *(?:- *(?P<to>[0-9]+))? *(?P<name>[^\n\r]+)", authors_raw, re.IGNORECASE):
            args = {
                'name': match.group('name'),
                'year_from': int(match.group('from'))
            }
            try:
                args['year_to'] = int(match.group('to'))
            except TypeError:
                args['year_to'] = args['year_from']
            author = Author(**args)
            self.authors.append(author)
        self.authors = sorted(self.authors, key=attrgetter('year_from'))


class Tool:
    """The license tool"""

    def __init__(self, default_license: License, default_author: Author,
                 company: str = None, aliases: Dict[str, str] = None):
        """Creates a new tool instance with default license and author"""
        self.default_license = default_license
        self.default_author = default_author
        self.aliases = aliases or {}
        self.company = company
        self.header = Header(self.default_license)

    @staticmethod
    def force_newline(input: str, newline='\n') -> str:
        """Change input to use the given newline and return the result"""
        if newline == '\n':
            # fast path, simply drop any remaining dos endings
            return input.replace('\r\n', '\n')
        # this requires to sweep the input twice but is the most
        # reliable way to catch all unix endings without the need
        # to use a look-behind regex (which would be even slower)
        return Tool.force_newline(input).replace('\n', newline)

    def bump(self, filename: pathlib.PurePath,
             keep_license: bool = True, custom_title: bool = False, keep_authors: bool = True) -> str:
        """
        Reads a file and returns the bumped contents
        :filename: The file to be bumped
        :keep_license: If an existing license should be retained or replaced with the new default
        :custom_title: Specifies a custom title to use instead of the filename
        :keep_authors: If any existing authors should be retained or replaced with the new default
        returns a tuple of detected language and bumped contents
        """
        parsed = ParsedHeader(filename)
        if parsed.style == Style.UNKNOWN:
            logging.warning(f"Failed to determine comment style for {filename}")
            return Style.UNKNOWN, None

        latest_author = None
        git_repo = self.default_author.git_repo
        if git_repo:
            # first try to test if the file has been cached
            if git_repo.is_modified_in_tree(filename):
                latest_author = self.default_author
            # try to determine the author using the git history of the file
            else:
                latest_author = git_repo.author_from_history(filename)

            if latest_author:
                # make sure to honor year_from coming from the config
                latest_author.year_from = min(latest_author.year_from, self.default_author.year_from)
                # make sure to honor a name override coming from the config
                if not self.default_author.name_from_git:
                    latest_author.name = self.default_author.name
        if latest_author is None:
            latest_author = self.default_author

        new_author = True
        for author in parsed.authors:
            alias = self.aliases.get(author.name, None)
            if latest_author.name in (author.name, alias):
                author.year_to = latest_author.year_to
                author.name = latest_author.name
                year_to = max(author.year_from, author.year_to)
                year_from = min(author.year_from, author.year_to)
                author.year_from = year_from
                author.year_to = year_to
                new_author = False
        if new_author:
            parsed.authors.append(latest_author)

        # make sure to deduplicate authors properly
        seen_authors = {}
        for author in parsed.authors:
            seen = seen_authors.get(author.name, None)
            if seen:
                seen.year_from = min(seen.year_from, author.year_from)
                seen.year_to = max(seen.year_to, author.year_to)
            else:
                seen_authors[author.name] = author
        if keep_authors:
            parsed.authors = list(seen_authors.values())
        else:
            parsed.authors = [latest_author]

        license_text = None
        if keep_license:
            license_text = parsed.license

        title = custom_title
        if not title:
            title = filename.name

        # the updated output is the new header with the remainder and ensuring a single trailing newline
        output = self.header.render(
            title, parsed.authors, parsed.style, company=self.company, license=license_text)
        output = output + '\n' + parsed.remainder + '\n'
        if parsed.decls:
            output = '\n'.join(parsed.decls) + '\n' + output
        output = Tool.force_newline(output, parsed.newline)
        return parsed.style, output

    def bump_inplace(self, filename: pathlib.PurePath, keep_license: bool = True,
                     custom_title: bool = False, simulate: bool = False, keep_authors: bool = True) -> bool:
        """
        Bumps the license header of a given file
        :filename: The file to be bumped
        :keep_license: If an existing license should be retained or replaced with the new default
        :custom_title: Use a custom title instead of the filename
        :simulate: Perform a dry run not applying any changes
        :keep_authors: If any existing authors should be retained or replaced with the new default
        """
        _, bumped = self.bump(filename, keep_license=keep_license, custom_title=custom_title, keep_authors=keep_authors)
        if bumped:
            filename = str(filename) + \
                '.license_bumped' if simulate else filename
            with open(filename, 'w', encoding='utf-8', newline='') as output:
                output.write(bumped)
                return True
        return False


class FileFilter:
    """Helper to filter against an exclude and include list"""

    @staticmethod
    @functools.lru_cache(maxsize=256, typed=True)
    def _glob_to_re(expr: str) -> re.Pattern:
        """
        Converts a globbing expression to a regex

        In contrast to fnmatch it supports recursive
        globbing as well and is cached similar to
        fnmatch.fnmatch is optimizing repeated calls.
        """
        class State(enum.Enum):
            '''Enumerates parsing state'''
            TEXT = 0
            SEQ = 1
            GLOB = 2

        state = State.TEXT
        pattern = '^'
        i, n = 0, len(expr)  # pylint: disable=invalid-name
        while i < n:
            # when in a sequence continue
            # up to the terminator
            if state == State.SEQ:
                if expr[i] == '[':
                    raise RuntimeError(f"Character sequences cannot be nested: {expr}")
                if expr[i] == ']':
                    pattern += ']'
                    state = State.TEXT
                else:
                    pattern += re.escape(expr[i])
            elif expr[i] == ']':
                raise RuntimeError(f"Closing sequence not opened before: {expr}")
            elif expr[i:i+2] == '[!':  # negated sequence
                state = State.SEQ
                pattern += '[^'
                i += 1
            elif expr[i] == '[':  # sequence
                state = State.SEQ
                pattern += '['
            elif expr[i:i+3] == '**/':  # recursive glob
                pattern += '(.+/)?'
                i += 2
            elif expr[i] == '?':  # single char
                pattern += '[^/]'
            elif expr[i] == '*':  # basic globbing
                if state != State.GLOB:
                    pattern += '[^/]*'
                    state = State.GLOB
                # else: Skip consecutive *
            else:
                pattern += re.escape(expr[i])
                state = State.TEXT
            i += 1
        pattern += '$'
        return re.compile(pattern)

    @staticmethod
    @functools.lru_cache(maxsize=256, typed=True)
    def _to_re(pattern: str) -> re.Pattern:
        return re.compile(pattern)

    @staticmethod
    def is_included(file_rel: str, includes, excludes) -> bool:
        """
        Tests if a given relative file matches includes and not excludes

        :file_rel: Relative filepath to be tested
        :includes: List of globbing expressions noting files to includes
        :exclude: List of regular expressions noting files to exclude
        """
        matched = False
        match_reason = f"Excluding '{file_rel}' - failed to match any"
        for include in includes:
            include = FileFilter._glob_to_re(include)
            if re.match(include, file_rel):
                match_reason = f"Including '{file_rel}' because of '{include.pattern}'"
                matched = True
                break
        for exclude in excludes:
            exclude = FileFilter._to_re(exclude)
            if re.search(exclude, file_rel):
                match_reason = f"Excluding '{file_rel}' due to '{exclude.pattern}'"
                matched = False
                break
        logging.debug(match_reason)
        return matched


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='license_tools',
        description=f'Helper to maintain current code license headers ({", ".join(LICENSES)}).')
    parser.add_argument('-v', '--verbose', help='Enable verbose logging',
                        action='store_true', default=False)
    parser.add_argument(
        '-c', '--config',
        help='Configuration to be loaded.'
        f' Will search for {LICENSE_JSON} in the current working dir or its parent if omitted',
        type=pathlib.Path,
        default=None)
    parser.add_argument(
        '-f', '--force-license',
        help='Ignore existing license headers and replace with the configured license instead',
        default=False, action='store_true')
    parser.add_argument(
        '--dry-run', help='Simulate and write to a sidecar file instead',
        default=False, action='store_true')
    parser.add_argument(
        '--sample-config', help='Generate a default configuration file to the working directory',
        default=False, action='store_true')
    parser.add_argument(
        'files', nargs='*', type=pathlib.Path,
        help='The file to be processed. Repeat to pass multiple.'
             ' Leave empty to process files in and below the current working directory.'
             ' Inclusions and exclusions from the config will always be considered.')
    args = parser.parse_args()

    format = '[%(levelname)s] %(message)s'
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=format)
    else:
        logging.basicConfig(level=logging.INFO, format=format)

    if args.sample_config:
        default_config = {
            'author': {
                'from_git': True,
                'years': [1970, DateUtils.current_year()],
                'name': '<author here>',
                'company': 'the authors',
                'aliases': {
                    '<old author name>': '<new author name>'
                }
            },
            'force_author': False,
            'license': f'<pick one of {", ".join(LICENSES.keys())}>',
            'force_license': False,
            "custom_license": False,
            'custom_title': False,
            'include': [
                '**/*'
            ],
            'exclude': [
                '^\\.[^/]+',
                '/\\.[^/]+'
            ]
        }
        with open(CW_DIR / LICENSE_JSON, 'w', encoding='utf-8') as configfile:
            configfile.write(json.dumps(default_config, indent=4))
            logging.info(f'Wrote default config to {CW_DIR / LICENSE_JSON}')
            sys.exit(0)

    if args.files:
        ret = handle_files(args, [file.resolve() for file in args.files])
    else:
        ret = handle_files(args, CW_DIR.glob('*'))
    if not ret:
        sys.exit(1)


def handle_files(args, candidates):
    """Processes a given set of candidates resolving dirs on the way"""
    success = True
    for candidate in candidates:
        if candidate.name == '.git':
            continue
        if candidate.is_dir():
            success = handle_files(args, candidate.rglob('*')) and success
        else:
            success = process_file(copy(args), candidate) and success
    return success


@functools.lru_cache(maxsize=256, typed=True)
def discover_config(level: pathlib.Path) -> pathlib.Path:
    """
    Searches the given level and any directories
    above for a LICENSE_JSON configuration file
    """
    config = None
    while config is None and level.parent != level:
        candidate = level / LICENSE_JSON
        if candidate.exists():
            config = candidate
        else:
            level = level.parent
    return config


@functools.lru_cache(maxsize=256, typed=True)
def parse_config(config: pathlib.Path) -> dict:
    """
    Tries to parse the given config
    """
    with open(config, 'r', encoding='utf-8') as configfile:
        try:
            return json.load(configfile)
        except json.JSONDecodeError as error:
            logging.fatal(f"Failed to parse config: {error}")
            sys.exit(2)


def process_file(args, file) -> bool:
    """
    Processes a single file honoring the discovered config

    Will return true on success, false on failure.
    If the file does not match the config this is considered success.
    """
    if args.config is None:
        args.config = discover_config(file.parent)
    if args.config:
        def try_shorten(path: pathlib.Path):
            try:
                return path.relative_to(CW_DIR)
            except ValueError:
                return path
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"Using '{try_shorten(args.config)}' to process '{try_shorten(file)}'")
    else:
        logging.fatal(f"Failed to discover a configuration for {file}")
        sys.exit(2)

    config_dir = args.config.parent
    config = parse_config(args.config)

    file_rel = file.relative_to(config_dir).as_posix()
    includes = config.get('include', ['**/*'])
    excludes = config.get('exclude', ['^\\.[^/]+', '/\\.[^/]+'])
    if not FileFilter.is_included(file_rel, includes, excludes):
        return True

    if 'custom_license' in config:
        license = License(custom=config['custom_license'])
    else:
        try:
            license = config.get('license', False)
            if license:
                license = License(builtin=license)
        except TypeError:
            valid = "\"" + "\", \"".join(LICENSES.keys()) + "\""
            logging.fatal(f"Invalid license '{license}' - supported licenses are {valid}")
            sys.exit(2)

    config_author = config.get('author', {})
    author = None
    if 'from_git' in config_author:
        try:
            git_repo = GitRepo(cwd=config_dir)
        except RuntimeError as error:
            logging.fatal(f"Not running within a git repo: {error}")
            sys.exit(2)
        try:
            author = git_repo.author_from_config()
        except RuntimeError as error:
            logging.fatal(f"Failed to fetch author from git as configured: {error}")
            sys.exit(2)
        logging.debug(f"New files will get author from git: \"{author.name}\"")
    if 'name' in config_author:
        if author is None:
            author = Author(config_author['name'])
        else:
            author.name = config_author['name']
            author.name_from_git = False
            logging.debug(f"Author was overridden: \"{author.name}\"")
    if author is None:
        logging.fatal("Please change config to explicitly specify or derive the author from git")
        sys.exit(2)
    if 'years' in config_author:
        years = config_author['years']
        if len(years) < 1 or len(years) > 2:
            logging.fatal(f"Please provide the 'years' attribute as [from] or pair [from, to]: {years}")
            sys.exit(2)
        try:
            years = [int(year) for year in years]
        except ValueError as error:
            logging.fatal(f"Please provide the 'years' attribute as numbers: {error}")
            sys.exit(2)
        year_from = min(years)
        year_to = max(years)
        if author.git_repo:
            author.year_from = min(year_from, author.year_from)
            author.year_to = max(year_to, author.year_to)
        else:
            author.year_from = year_from
            author.year_to = year_to
    aliases = config_author.get('aliases', {})

    custom_title = config.get('custom_title', False)
    company = config_author.get('company', None)
    tool = Tool(license, author, company, aliases)
    keep_license = not args.force_license and not config.get('force_license', False)
    keep_authors = not config.get('force_author', False)

    logging.debug(f"Processing '{file_rel}'")
    try:
        if tool.bump_inplace(file, keep_license=keep_license, keep_authors=keep_authors, custom_title=custom_title, simulate=args.dry_run):
            return True
    except UnicodeDecodeError as error:
        logging.warning(f"Failed to decode {file_rel}: {error}")
    return False
