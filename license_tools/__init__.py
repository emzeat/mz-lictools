"""
 __init__.py

 Copyright (c) 2012 - 2021 Marius Zwicker
 All rights reserved.

 @LICENSE_HEADER_START@
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
 @LICENSE_HEADER_END@
"""

from operator import attrgetter
import argparse
import datetime
import enum
import json
import pathlib
import re
import subprocess
import sys
import jinja2

BASE_DIR = pathlib.Path(__file__).parent
LICENSES = [license_file.stem for license_file in BASE_DIR.glob('*.erb')]


class Style(enum.Enum):
    """Enumerates the different known comment styles"""
    UNKNOWN = 1
    C_STYLE = 2
    POUND_STYLE = 3
    DOCSTRING_STYLE = 4

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
            '.java': Style.C_STYLE,
            '.rb': Style.POUND_STYLE,
            '.py': Style.DOCSTRING_STYLE,
            '.sh': Style.POUND_STYLE,
            '.bash': Style.POUND_STYLE,
            '.command': Style.POUND_STYLE,
            '.cmake': Style.POUND_STYLE
        }
        return mapping.get(ext, Style.UNKNOWN)

    @staticmethod
    def patterns():
        """
        Returns a list of regex and style pairs

        Each regex has two match groups, one for the license and one for the remainder
        """
        return [
            (Style.C_STYLE, r"\* +@LICENSE_HEADER_START@(.+)\* +@LICENSE_HEADER_END@(?:.*?)\*/(.*)"),
            (Style.POUND_STYLE, r"# +@LICENSE_HEADER_START@(.+)# +@LICENSE_HEADER_END@(?:.*?)#\n(.*)"),
            (Style.DOCSTRING_STYLE, r"@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(?:.*?)\n\"\"\"(.*)"),
            (Style.UNKNOWN, r"@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(.*)")
        ]


class Author:
    """Describes an author of a file"""

    def __init__(self, name: str, year_from: int = None,
                 year_to: int = datetime.date.today().year):
        """
        Creates a new author
        :name: The name of the author
        :year_from: The first year the author contributed
        :year_to: The last year the author contributed
        """
        self.name = name
        self.year_to = year_to
        if year_from:
            self.year_from = year_from
        else:
            self.year_from = year_to


class License:
    """Describes a license to be added to a header"""

    def __init__(self, name: str):
        """
        Creates a new license

        The name needs to be one of the supported licenses
        """
        self.name = name
        self.header = name + '.erb'
        if not (BASE_DIR / self.header).exists():
            raise TypeError("No such license")


class Header:
    """Describes a header to be rendered with license and authors"""

    def __init__(self, default_license):
        """Creates a new header using given default license"""
        loader = jinja2.FileSystemLoader(BASE_DIR)
        self.env = jinja2.Environment(loader=loader)
        self.template = self.env.get_template('Header.j2')
        self.default_license = default_license

    def render(self, filename: str, authors, style: Style, company: str = None, license: str = None) -> str:
        """
        Renders a header to a string
        :filename: The file the header belongs to
        :authors: A list of authors which contributed to the file
        :style: The comment style to use when generating the header
        :company: An optional company string to be included
        :license: An optional license string to be used, if omitted the default_license will apply
        """
        if company is None:
            company = authors[-1].name
        header = self.template.render(default_license=self.default_license.header,
                                      license=license, filename=filename, authors=authors, company=company)
        header = header.split('\n')
        if style == Style.C_STYLE:
            header = ['/*'] + \
                     ['* ' + h if h.strip() else '*' for h in header] + ['*/', '']
        elif style == Style.POUND_STYLE:
            header = ['#'] + \
                     ['# ' + h if h.strip() else '#' for h in header] + ['#', '']
        elif style == Style.DOCSTRING_STYLE:
            header = ['"""'] + \
                     [' ' + h if h.strip() else '' for h in header] + ['"""', '']
        return '\n'.join(header)


class ParsedHeader:
    """A license header parsed from an existing file"""

    def __init__(self, file: pathlib.PurePath = None):
        """Parses a header from the given file"""
        with open(file, 'r', encoding='utf-8') as file_obj:
            contents = file_obj.read()
        # style is determined from the extension, if unknown we try a second attempt using the contents below
        self.style = Style.from_suffix(file.suffix)
        # retain any shebang and encoding at the beginning
        self.shebang = re.match(r'^#!.+(\n# -\*-.+)?', contents, re.MULTILINE)
        if self.shebang:
            self.shebang = self.shebang[0]
        else:
            self.shebang = re.match(r'^# -\*-.+', contents)
            if self.shebang:
                self.shebang = self.shebang[0]
        # use a regex to extract existing authors, i.e. any line starting with 'Copyright'
        self.authors = []
        for match in re.findall(r"(?<!\w) Copyright[^\d]*([0-9]+) *(?:- *([0-9]+))? *([\w \.]+)", contents):
            if len(match) == 3:
                args = {
                    'name': match[2],
                    'year_from': int(match[0])
                }
                try:
                    args['year_to'] = int(match[1])
                except ValueError:
                    args['year_to'] = args['year_from']
                author = Author(**args)
                self.authors.append(author)
        self.authors = sorted(self.authors, key=attrgetter('year_from'))
        # any known license is wrapped in well-known tags
        for style, pattern in Style.patterns():
            match = re.search(pattern, contents, re.MULTILINE | re.DOTALL)
            if match:
                if style != Style.UNKNOWN:
                    self.style = style
                break
        if match:
            self.license = re.sub(r'[#\*] ?', '', match[1], flags=re.MULTILINE).strip('\n\r')
            if self.license.startswith(' '):
                # filter any leading indends
                self.license = self.license.replace('\n ', '\n')
            self.license = self.license.strip()
            self.remainder = match[2].strip()
        else:
            self.license = None
            self.remainder = contents.strip()


class Tool:
    """The license tool"""

    def __init__(self, default_license: License, default_author: Author):
        """Creates a new tool instance with default license and author"""
        self.this_year = datetime.date.today().year
        self.default_license = default_license
        self.default_author = default_author
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
            print(f"Failed to determine comment style for {filename}")
            return Style.UNKNOWN, None

        new_author = True
        for author in parsed.authors:
            if author.name == self.default_author.name:
                author.year_to = self.this_year
                new_author = False
        if new_author:
            parsed.authors.append(self.default_author)

        license_text = None
        if keep_license:
            license_text = parsed.license

        # the updated output is the new header with the remainder and ensuring a single trailing newline
        output = self.header.render(
            filename.name, parsed.authors, parsed.style, license=license_text)
        output = output + '\n' + parsed.remainder + '\n'
        if parsed.shebang:
            output = parsed.shebang + '\n' + output
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
        '-s', '--simulate', help='Simulate and write to a sidecar file instead',
        default=False, action='store_true')
    parser.add_argument(
        'files', nargs='*', type=pathlib.Path,
        help='The file to be processed. Repeat to pass multiple. Pass none to process current working directory')
    args = parser.parse_args()

    cwd = pathlib.Path.cwd()
    level = cwd
    while args.config is None and level.parent != level:
        config = level / license_json
        if config.exists():
            args.config = config
        else:
            level = level.parent
    if args.config:
        print(f"Using configuration from '{args.config}'")
    else:
        parser.print_help()
        parser.error("Failed to discover configuration")

    with open(args.config, 'r', encoding='utf-8') as configfile:
        config = json.load(configfile)

    try:
        license = License(config.get('license', None))
    except TypeError:
        valid = "\"" + "\", \"".join(LICENSES) + "\""
        print(f"Invalid license, supported licenses are {valid}")
        sys.exit(2)

    config_author = config.get('author', {})
    if 'name' in config_author:
        author = Author(config_author['name'])
    elif 'from_git' in config_author:
        try:
            git_author = subprocess.check_output(
                'git config user.name', stderr=subprocess.STDOUT, shell=True)
            git_author = git_author.decode().strip()
        except subprocess.CalledProcessError as error:
            print(f"Failed to fetch author using git: {error.output}")
        print(f"Using author from git: \"{git_author}\"")
        author = Author(git_author)

    tool = Tool(license, author)
    keep = not args.force_license
    failed = False

    for expr in config.get('update', []):
        for file in cwd.glob(expr):
            file_rel = file.relative_to(cwd)
            if args.files and file_rel not in args.files:
                continue
            print(f"+ Processing \"{file_rel}\"")
            if not tool.bump_inplace(file, keep_license=keep, simulate=args.simulate):
                failed = True

    if failed:
        sys.exit(1)
