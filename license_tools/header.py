# header.py
#
# Copyright (c) 2012 - 2025 Marius Zwicker
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

"""
Description of a license header
"""

import os
import pathlib
import re
from operator import attrgetter
import jinja2

from .style import Style
from .utils import DateUtils
from .license import BASE_DIR


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
            git_author_date = os.environ.get('GIT_AUTHOR_DATE', None)
            if self.name_from_git and git_author_date:
                year_to = DateUtils.parse_git_date(git_author_date).year
            else:
                year_to = DateUtils.current_year()
        self.year_to = year_to
        if year_from:
            self.year_from = year_from
        else:
            self.year_from = year_to

    def __repr__(self) -> str:
        return f"({self.name} {self.year_from}-{self.year_to})"

    def __eq__(self, other: object) -> bool:
        return self.name == other.name and self.year_from == other.year_from and self.year_to == other.year_to


class Title:
    """Describes the title to be added to a header"""

    BUILTINS = ['filename', 'at_file_filename', 'backslash_file_filename']

    def __init__(self, builtin: str = None, custom: str = None):
        """
        Creates a new title

        Either builtin or custom need to be specified.

        :builtin: One of the builtin titles, see BUILTINS
        :custom: Configures a custom title text
        """
        self.filename = False
        self.prefix = None
        if builtin == 'filename':
            self.filename = True
        elif builtin == '@file':
            self.filename = True
            self.prefix = '@file '
        elif builtin == '\\file':
            self.filename = True
            self.prefix = '\\file '
        elif custom:
            self.custom = custom
        else:
            raise KeyError("Need to select a 'builtin' or provide 'custom' title")

    def get(self, file: pathlib.Path) -> str:
        '''Determines the title for the given file'''
        if self.filename:
            title = file.name
        else:
            title = self.custom
        if self.prefix:
            title = self.prefix + title
        return title


class Header:
    """Describes a header to be rendered with license and authors"""

    def __init__(self, default_license, lines_after_license: int = 1):
        """Creates a new header using given default license"""
        loader = jinja2.FileSystemLoader(BASE_DIR)
        self.env = jinja2.Environment(loader=loader)
        self.template = self.env.get_template('Header.j2')
        self.default_license = default_license
        self.lines_after_license = lines_after_license

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
        header = [f'{decorators.prefix} ' + h if h.strip() else decorators.prefix for h in header]
        if decorators.start:
            header = [decorators.start] + header
        if decorators.end:
            header = header + [decorators.end]
        return '\n'.join(header) + '\n' * max(self.lines_after_license, 1)


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
        if isinstance(file, str):
            file = pathlib.Path(file)
        # keep the original contents for book keeping
        self.orig_contents = contents
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
                match_style = style
                if self.style == Style.UNKNOWN:
                    self.style = style
                break
        if match:
            # grab the matched license but remove any # or * per line prefix decorators
            self.license = match.group('license')
            decorators = Style.decorators(match_style)
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
