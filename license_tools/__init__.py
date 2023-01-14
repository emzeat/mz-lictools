"""
 __init__.py

 Copyright (c) 2012 - 2023 Marius Zwicker
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

import argparse
import datetime
import enum
import json
import logging
import pathlib
import re
import subprocess
import sys
import os
from collections import namedtuple
from operator import attrgetter
from typing import Dict
import jinja2

BASE_DIR = pathlib.Path(__file__).parent
SPDX_LICENSES = list(BASE_DIR.glob('*.spdx'))
OTHER_LICENSES = list(BASE_DIR.glob('*.license'))
LICENSES = {license_file.stem: license_file for license_file in SPDX_LICENSES + OTHER_LICENSES}


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
            '.rc': Style.SLASH_STYLE
        }
        return mapping.get(ext, Style.UNKNOWN)

    @staticmethod
    def patterns():
        """
        Returns a list of regex and style pairs

        Each regex has two match groups, one for the license and one for the remainder
        """
        return [
            (Style.C_STYLE,
                r"\*(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)\* +@LICENSE_HEADER_END@(?:.*?)\*/(?P<body>.*)"),
            (Style.C_STYLE,
                r"\*(?P<authors>.+?)@MLBA_OPEN_LICENSE_HEADER_START@(?P<license>.+?)\* +@MLBA_OPEN_LICENSE_HEADER_END@(?:.*?)\*/(?P<body>.*)"),
            (Style.C_STYLE,
                r"\*(?P<authors>.+?)All rights reserved\.(?P<license>.+?)\*/(?P<body>.*)"),
            (Style.POUND_STYLE,
                r"#(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)# +@LICENSE_HEADER_END@(?:.*?)#\n(?P<body>.*)"),
            (Style.POUND_STYLE,
                r"#(?P<authors>.+?)All rights reserved\.(?P<license>.+?)#\n[^#](?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"\"\"\"\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\n\"\"\"(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"\"\"\"\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)\"\"\"\n(?P<body>.*)"),
            (Style.XML_STYLE,
                r"<!--\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\n-->(?P<body>.*)"),
            (Style.XML_STYLE,
                r"<!--\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)-->\n(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"REM(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)REM\n(?!REM)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"REM(?P<authors>.+?)All rights reserved\.(?P<license>.+?)REM\n(?!REM)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"::(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)::\n(?!::)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"::(?P<authors>.+?)All rights reserved\.(?P<license>.+?)::\n(?!::)(?P<body>.*)"),
            (Style.SLASH_STYLE,
                r"//(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)// +@LICENSE_HEADER_END@(?:.*?)//\n(?P<body>.*)"),
            (Style.SLASH_STYLE,
                r"//(?P<authors>.+?)All rights reserved\.(?P<license>.+?)//\n[^//](?P<body>.*)"),
            (Style.UNKNOWN,
                r"(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?P<body>.*)"),
        ]

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
            return Decorator('"""', '', '"""', None)
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
        if year_to is None:
            year_to = DateUtils.current_year()
        self.year_to = year_to
        if year_from:
            self.year_from = year_from
        else:
            self.year_from = year_to


class GitRepo:
    """Git repository object"""

    def __init__(self):
        """
        Creates a repository object using the current working dir to determine the root

        :throws RuntimeError: When failing to detect the root
        """
        try:
            self.git_root = subprocess.check_output(
                'git rev-parse --show-toplevel', stderr=subprocess.STDOUT, shell=True, encoding='utf-8')
            self.git_root = pathlib.Path(self.git_root.strip())
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"Not a git repo: {error.output}") from error

    def author_from_config(self) -> Author:
        """Returns the author as set via gitconfig"""
        try:
            git_author = subprocess.check_output(
                'git config user.name', stderr=subprocess.STDOUT, shell=True, encoding='utf-8')
            git_author = git_author.strip()
            return Author(git_author, git_repo=self)
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
                logging.debug(f"{file_rel} was just modified\": {diff}")
                return True
        except subprocess.CalledProcessError:
            pass
        return False


class License:
    """Describes a license to be added to a header"""

    def __init__(self, name: str):
        """
        Creates a new license

        The name needs to be one of the supported licenses
        """
        self.name = name
        self.header = LICENSES.get(name, None)
        if self.header is None:
            raise TypeError(f"No such license '{name}'")
        self.spdx = self.header in SPDX_LICENSES
        self.header = self.header.name


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

    def __init__(self, file: pathlib.PurePath = None):
        """Parses a header from the given file"""
        with open(file, 'r', encoding='utf-8') as file_obj:
            contents = file_obj.read()
        # style is determined from the extension, if unknown we try a second attempt using the contents below
        self.style = Style.from_suffix(file.suffix)
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
        for style, pattern in Style.patterns():
            match = re.search(pattern, contents, re.MULTILINE | re.DOTALL)
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
            self.remainder = match.group('body').strip()
        else:
            self.license = None
            self.remainder = contents.strip()
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

    def bump(self, filename: pathlib.PurePath,
             keep_license: bool = True) -> str:
        """
        Reads a file and returns the bumped contents
        :filename: The file to be bumped
        :keep_license: If an existing license should be retained or replaced with the new default
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
        parsed.authors = list(seen_authors.values())

        license_text = None
        if keep_license:
            license_text = parsed.license

        # the updated output is the new header with the remainder and ensuring a single trailing newline
        output = self.header.render(
            filename.name, parsed.authors, parsed.style, company=self.company, license=license_text)
        output = output + '\n' + parsed.remainder + '\n'
        if parsed.decls:
            output = '\n'.join(parsed.decls) + '\n' + output
        return parsed.style, output

    def bump_inplace(self, filename: pathlib.PurePath, keep_license: bool = True,
                     simulate: bool = False) -> bool:
        """
        Bumps the license header of a given file
        :filename: The file to be bumped
        :keep_license: If an existing license should be retained or replaced with the new default
        """
        _, bumped = self.bump(filename, keep_license=keep_license)
        if bumped:
            filename = str(filename) + \
                '.license_bumped' if simulate else filename
            with open(filename, 'w', encoding='utf-8') as output:
                output.write(bumped)
                return True
        return False


def main():
    """CLI entry point"""
    license_json = '.license-tools-config' \
                   '.json'
    parser = argparse.ArgumentParser(
        prog='license_tools',
        description=f'Helper to maintain current code license headers ({", ".join(LICENSES)}).')
    parser.add_argument('-v', '--verbose', help='Enable verbose logging',
                        action='store_true', default=False)
    parser.add_argument(
        '-c', '--config',
        help='Configuration to be loaded.'
        f' Will search for {license_json} in the current working dir or its parent if omitted',
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

    cwd = pathlib.Path.cwd()
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
            'license': f'<pick one of {", ".join(LICENSES.keys())}>',
            'force_license': False,
            'include': [
                '**/*'
            ],
            'exclude': [
                '^\\.[^/]+',
                '/\\.[^/]+'
            ]
        }
        with open(cwd / license_json, 'w', encoding='utf-8') as configfile:
            configfile.write(json.dumps(default_config, indent=4))
            logging.info(f'Wrote default config to {cwd / license_json}')
            sys.exit(0)

    level = cwd
    while args.config is None and level.parent != level:
        config = level / license_json
        if config.exists():
            args.config = config
        else:
            level = level.parent
    if args.config:
        logging.info(f"Using configuration from '{args.config}'")
    else:
        parser.error("Failed to discover a configuration")

    config_dir = args.config.parent
    with open(args.config, 'r', encoding='utf-8') as configfile:
        try:
            config = json.load(configfile)
        except json.JSONDecodeError as error:
            logging.fatal(f"Failed to parse config: {error}")
            sys.exit(2)

    try:
        license = License(config.get('license', None))
    except TypeError:
        valid = "\"" + "\", \"".join(LICENSES.keys()) + "\""
        logging.fatal(f"Invalid license, supported licenses are {valid}")
        sys.exit(2)

    config_author = config.get('author', {})
    if 'name' in config_author:
        author = Author(config_author['name'])
    elif 'from_git' in config_author:
        try:
            git_repo = GitRepo()
        except RuntimeError as error:
            logging.fatal(f"Not running within a git repo: {error}")
            sys.exit(2)
        try:
            author = git_repo.author_from_config()
        except RuntimeError as error:
            logging.fatal(f"Failed to fetch author from git as configured: {error}")
            sys.exit(2)
        logging.info(f"New files will get author from git: \"{author.name}\"")
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

    if args.files:
        args.files = [file.resolve() for file in args.files]

    company = config_author.get('company', None)
    tool = Tool(license, author, company, aliases)
    keep = not args.force_license and not config.get('force_license', False)
    failed = False
    excludes = [re.compile(excl) for excl in config.get('exclude', ['^\\.[^/]+', '/\\.[^/]+'])]

    for include in config.get('include', ['**/*']):
        logging.debug(f"Pattern '{include}'")
        for file in config_dir.glob(include):
            if file.is_dir():
                continue
            file_rel = file.relative_to(config_dir)
            logging.debug(f"Candidate '{file_rel}'")
            if args.files and file not in args.files:
                logging.debug(f"Excluding '{file_rel}' because not in args")
                continue
            excluded = False
            for exclude in excludes:
                if re.search(exclude, str(file_rel)):
                    logging.debug(f"Excluding '{file_rel}' due to '{exclude}'")
                    excluded = True
                    break
            if excluded:
                continue
            logging.debug(f"Processing '{file_rel}'")
            try:
                if not tool.bump_inplace(file, keep_license=keep, simulate=args.dry_run):
                    failed = True
            except UnicodeDecodeError as error:
                logging.warning(f"Failed to decode {file_rel}: {error}")
                failed = True

    if failed:
        sys.exit(1)
