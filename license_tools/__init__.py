import datetime

import jinja2
import pathlib
import datetime
import re
import enum
from operator import attrgetter

BASE_DIR = pathlib.Path(__file__).parent
LICENSES = [license_file.stem for license_file in BASE_DIR.glob('*.erb')]


class Style(enum.Enum):
    UNKNOWN = 1
    C_STYLE = 2
    POUND_STYLE = 3


class Author:
    def __init__(self, name: str, year_from: int = None, year_to: int = datetime.date.today().year):
        self.name = name
        self.year_from = year_from
        self.year_to = year_to


class License:
    def __init__(self, name: str):
        self.name = name
        with open(BASE_DIR / (name + '.erb'), 'r') as license_file:
            self.contents = license_file.read()


class ParsedHeader:
    def __init__(self, input: str = None, file: pathlib.PurePath = None):
        # if no input read the file instead
        if input is None:
            if file is None:
                raise NotImplementedError(
                    "Need either input string or filepath")
            with open(file, 'r') as contents:
                input = contents.read()
        # use a regex to extract existing authors, i.e. any line starting with 'Copyright'
        self.authors = []
        for match in re.findall(r'Copyright[^\d]*([0-9]+) *(?:- *([0-9]+))? *([\w \.]+)', input):
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
        # the type is determined when matching the remainder of the file
        style = re.search(
            r'/*(?:.*)@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(?:.*)\*/(.*)', input, re.MULTILINE | re.DOTALL)
        if style:
            self.style = Style.C_STYLE
        else:
            style = re.search(
                r'#(?:.*)@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(?:.*)#\n(.*)', input, re.MULTILINE | re.DOTALL)
            if style:
                self.style = Style.POUND_STYLE
            else:
                raise NotImplementedError(
                    "Unknown code style, cannot update license")
        self.license = re.sub(r'^. ', '', style[1], flags=re.MULTILINE).strip()
        self.remainder = style[2].strip()
        pass


class Header:
    def __init__(self, license: License, author: Author):
        self.license = license
        self.author = author

    def bump(self, input: str) -> str:
        parsed = ParsedHeader(input)
        pass
