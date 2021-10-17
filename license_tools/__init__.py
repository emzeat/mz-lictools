#
# __init__.py
#
# Copyright (c) 2021 Marius Zwicker
# All rights reserved.
#
# @LICENSE_HEADER_START@
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
# @LICENSE_HEADER_END@
#

import jinja2
import pathlib
import datetime
import re
import enum
import sys
import json
import argparse
import subprocess
from operator import attrgetter

BASE_DIR = pathlib.Path(__file__).parent
LICENSES = [license_file.stem for license_file in BASE_DIR.glob('*.erb')]


class Style(enum.Enum):
    UNKNOWN = 1
    C_STYLE = 2
    POUND_STYLE = 3

    @staticmethod
    def from_suffix(ext):
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
            '.py': Style.POUND_STYLE,
            '.sh': Style.POUND_STYLE,
            '.bash': Style.POUND_STYLE,
            '.command': Style.POUND_STYLE,
            '.cmake': Style.POUND_STYLE
        }
        return mapping.get(ext, Style.UNKNOWN)


class Author:
    def __init__(self, name: str, year_from: int = None, year_to: int = datetime.date.today().year):
        self.name = name
        self.year_to = year_to
        if year_from:
            self.year_from = year_from
        else:
            self.year_from = year_to


class License:
    def __init__(self, name: str):
        self.name = name
        self.header = name + '.erb'
        if not (BASE_DIR / self.header).exists():
            raise TypeError("No such license")


class Header:
    def __init__(self, default_license):
        loader = jinja2.FileSystemLoader(BASE_DIR)
        self.env = jinja2.Environment(loader=loader)
        self.template = self.env.get_template('Header.j2')
        self.default_license = default_license

    def render(self, filename: str, authors, style: Style, company: str = None, license: str = None) -> str:
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
        return '\n'.join(header)


class ParsedHeader:
    def __init__(self, file: pathlib.PurePath = None):
        with open(file, 'r') as file_obj:
            contents = file_obj.read()
        # style is determined from the extension, if unknown we try a second attempt using the contents below
        self.style = Style.from_suffix(file.suffix)
        # retain any shebang at the beginning
        self.shebang = re.match(r'^#!.+', contents)
        if self.shebang:
            self.shebang = self.shebang[0]
        # use a regex to extract existing authors, i.e. any line starting with 'Copyright'
        self.authors = []
        for match in re.findall(r"(?<!\w) Copyright[^\d]*([0-9]+) *(?:- *([0-9]+))? *([\w \.]+)", contents):
            if 3 == len(match):
                kw = dict()
                kw['name'] = match[2]
                kw['year_from'] = int(match[0])
                try:
                    kw['year_to'] = int(match[1])
                except ValueError:
                    kw['year_to'] = kw['year_from']
                author = Author(**kw)
                self.authors.append(author)
        self.authors = sorted(self.authors, key=attrgetter('year_from'))
        # any known license is wrapped in well-known tags
        # try to guess a c-style
        style = re.search(
            r"\* +@LICENSE_HEADER_START@(.+)\* +@LICENSE_HEADER_END@(?:.*?)\*/(.*)", contents, re.MULTILINE | re.DOTALL)
        if style:
            self.style = Style.C_STYLE
        else:
            # try to guess a pound-style
            style = re.search(
                r"# +@LICENSE_HEADER_START@(.+)# +@LICENSE_HEADER_END@(?:.*?)#\n(.*)", contents,
                re.MULTILINE | re.DOTALL)
            if style:
                self.style = Style.POUND_STYLE
            else:
                # no style determination possible
                style = re.search(
                    r'@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(.*)', contents,
                    re.MULTILINE | re.DOTALL)
        if style:
            self.license = re.sub(
                r'[#\*] ?', '', style[1], flags=re.MULTILINE).strip()
            self.remainder = style[2].strip()
        else:
            self.license = None
            self.remainder = contents.strip()
        pass


class Tool:
    def __init__(self, default_license: License, default_author: Author):
        self.this_year = datetime.date.today().year
        self.default_license = default_license
        self.default_author = default_author
        self.header = Header(self.default_license)

    def bump(self, filename: pathlib.PurePath, keep_license: bool = True) -> str:
        parsed = ParsedHeader(filename)
        if parsed.style == Style.UNKNOWN:
            print(f"Failed to determine comment style for {filename}")
            return None

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
        return output

    def bump_inplace(self, filename: pathlib.PurePath, keep_license: bool = True, simulate: bool = False) -> bool:
        bumped = self.bump(filename, keep_license=keep_license)
        if bumped:
            filename = str(filename) + \
                '.license_bumped' if simulate else filename
            with open(filename, 'w') as output:
                output.write(bumped)
                return True
        return False


def main():
    license_json = '.license-tools-config' \
                   '.json'
    parser = argparse.ArgumentParser(
        prog='license_tools',
        description='Helper to maintain current code license headers')
    parser.add_argument(
        '-c', '--config', help=f'Configuration to be loaded, will search for {license_json} in the current working dir or its parent if omitted', default=None)
    parser.add_argument('-f', '--force-license',
                        help='Ignore existing license headers and replace with the configured license instead', default=False, action='store_true')
    parser.add_argument('-s', '--simulate', help='Simulate and write to a sidecar file instead',
                        default=False, action='store_true')
    parser.add_argument('files', nargs='*', type=pathlib.Path,
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

    with open(args.config, 'r') as configfile:
        config = json.load(configfile)

    try:
        license = License(config.get('license', None))
    except TypeError:
        valid = "\"" + "\", \"".join(LICENSES) + "\""
        print(f"Invalid license, supported licenses are {valid}")
        sys.exit(2)

    config_author = config.get('author', dict())
    if 'name' in config_author:
        author = Author(config_author['name'])
    elif 'from_git' in config_author:
        try:
            git_author = subprocess.check_output(
                'git config user.name', stderr=subprocess.STDOUT, shell=True)
            git_author = git_author.decode().strip()
        except subprocess.CalledProcessError as e:
            print(f"Failed to fetch author using git: {e.output}")
        print(f"Using author from git: \"{git_author}\"")
        author = Author(git_author)

    tool = Tool(license, author)
    keep = False if args.force_license else True
    failed = False
    if args.files:
        for f in args.files:
            f = f.resolve()
            if not f.exists():
                print(f"Bad inputfile \"{f.relative_to(cwd)}\"")
                sys.exit(1)
            print(f"+ Processing \"{f.relative_to(cwd)}\"")
            if not tool.bump_inplace(f, keep_license=keep, simulate=args.simulate):
                failed = True
    else:
        for expr in config.get('update', []):
            for f in cwd.glob(expr):
                print(f"+ Processing \"{f.relative_to(cwd)}\"")
                if not tool.bump_inplace(f, keep_license=keep, simulate=args.simulate):
                    failed = True
    if failed:
        sys.exit(1)
