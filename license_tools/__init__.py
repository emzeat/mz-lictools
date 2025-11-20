# __init__.py
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
See README.md for detail and documentation
"""

import argparse
import functools
import json
import logging
import pathlib
import sys
from copy import copy
from typing import Dict

from .style import Style
from .utils import DateUtils, FileFilter, TextUtils
from .license import License, LICENSES
from .git import GitRepo
from .header import Header, ParsedHeader, Author, Title

BASE_DIR = pathlib.Path(__file__).parent
CW_DIR = pathlib.Path.cwd()
LICENSE_JSON = '.license-tools-config.json'


class Tool:
    """The license tool"""

    def __init__(self, default_license: License, default_author: Author,
                 company: str = None, aliases: Dict[str, str] = None, lines_after_license: int = 1):
        """Creates a new tool instance with default license and author"""
        self.default_license = default_license
        self.default_author = default_author
        self.aliases = aliases or {}
        self.company = company
        self.header = Header(self.default_license, lines_after_license)
        self.ignore_whitespace = lines_after_license < 0

    def bump(self, filename: pathlib.PurePath,
             keep_license: bool = True, title: Title = None, keep_authors: bool = True, latest_year_only: bool = False) -> str:
        """
        Reads a file and returns the bumped contents
        :filename: The file to be bumped
        :keep_license: If an existing license should be retained or replaced with the new default
        :title: The title to use in the header
        :keep_authors: If any existing authors should be retained or replaced with the new default
        :latest_year_only: Only lists the last year a file was touched
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
        if latest_year_only:
            for author in parsed.authors:
                author.year_from = author.year_to

        license_text = None
        if keep_license:
            license_text = parsed.license

        title_text = None
        if title:
            title_text = title.get(filename)

        # the updated output is the new header with the remainder and ensuring a single trailing newline
        output = self.header.render(
            title=title_text, authors=parsed.authors, style=parsed.style, company=self.company, license=license_text)
        if parsed.remainder:
            output = output + '\n'
        else:
            output = output.strip() + '\n'
        if parsed.decls:
            output = '\n'.join(parsed.decls) + '\n' + output
        output = TextUtils.force_newline(output, parsed.newline)
        if parsed.remainder:
            output = output + parsed.remainder + parsed.newline

        # compare old and new contents optionally ignoring any change in pure whitespace
        # so we play more nice with other linting tools
        if self.ignore_whitespace and not TextUtils.is_different_ignoring_ws(parsed.orig_contents, output):
            return parsed.style, parsed.orig_contents
        return parsed.style, output

    def bump_inplace(self, filename: pathlib.PurePath, keep_license: bool = True,
                     title: Title = None, simulate: bool = False, keep_authors: bool = True, latest_year_only: bool = False) -> bool:
        """
        Bumps the license header of a given file
        :filename: The file to be bumped
        :keep_license: If an existing license should be retained or replaced with the new default
        :title: The title to use in the header
        :simulate: Perform a dry run not applying any changes
        :keep_authors: If any existing authors should be retained or replaced with the new default
        :latest_year_only: Only lists the last year a file was touched
        """
        _, bumped = self.bump(filename, keep_license=keep_license, title=title,
                              keep_authors=keep_authors, latest_year_only=latest_year_only)
        if bumped:
            filename = str(filename) + \
                '.license_bumped' if simulate else filename
            with open(filename, 'w', encoding='utf-8', newline='') as output:
                output.write(bumped)
                return True
        return False


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
                'latest_year_only': False,
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
            'title': f'<pick one of {", ".join(Title.BUILTINS)} or leave out>',
            'custom_title': False,
            'lines_after_license': 1,
            'style_override_for_suffix': {
                ".cpp": f'<pick one of {", ".join([s.name for s in list(Style)])} or leave out>',
            },
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
    else:
        # Resolve relative config paths to absolute paths
        args.config = args.config.resolve()
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

    if 'custom_title' in config:
        title = Title(custom=config['custom_title'])
    else:
        try:
            title = config.get('title', 'filename')
            if title:
                title = Title(builtin=title)
        except TypeError:
            valid = "\"" + "\", \"".join(Title.BUILTINS) + "\""
            logging.fatal(f"Invalid title '{title}' - supported titles are {valid}")
            sys.exit(2)

    if 'style_override_for_suffix' in config:
        Style.set_overrides(config['style_override_for_suffix'])
    else:
        Style.set_overrides(None)

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
        if not isinstance(years, list) or len(years) < 1 or len(years) > 2:
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

    try:
        lines_after_license = config.get('lines_after_license', 1)
        if 'ignore' == lines_after_license:
            lines_after_license = -1
        else:
            lines_after_license = int(lines_after_license)
    except ValueError as error:
        logging.fatal(f"Please provide the 'lines_after_license' attribute as integer or use 'ignore': {error}")
        sys.exit(2)

    company = config_author.get('company', None)
    tool = Tool(license, author, company, aliases, lines_after_license)
    keep_license = not args.force_license and not config.get('force_license', False)
    keep_authors = not config.get('force_author', False)
    latest_year_only = config_author.get('latest_year_only', False)

    logging.debug(f"Processing '{file_rel}'")
    try:
        if tool.bump_inplace(file, keep_license=keep_license, keep_authors=keep_authors, latest_year_only=latest_year_only, title=title, simulate=args.dry_run):
            return True
    except UnicodeDecodeError as error:
        logging.warning(f"Failed to decode {file_rel}: {error}")
    return False
