
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
        self.year_from = year_from
        self.year_to = year_to


class License:
    def __init__(self, name: str):
        self.name = name
        self.header = name + '.erb'


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
            header = ['/*'] + ['* ' + h if h else '*' for h in header] + ['/*']
        elif style == Style.POUND_STYLE:
            header = ['#'] + ['# ' + h if h else '#' for h in header] + ['#']
        return '\n'.join(header)


class ParsedHeader:
    def __init__(self, file: pathlib.PurePath = None):
        with open(file, 'r') as file_obj:
            contents = file_obj.read()
        # style is determined from the extension, if unknown we try a second attempt using the contents below
        self.style = Style.from_suffix(file.suffix)
        # use a regex to extract existing authors, i.e. any line starting with 'Copyright'
        self.authors = []
        for match in re.findall(r"Copyright[^\d]*([0-9]+) *(?:- *([0-9]+))? *([\w \.]+)", contents):
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
            r"/*(?:.*)@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(?:.*)\*/(.*)", contents, re.MULTILINE | re.DOTALL)
        if style:
            self.style = Style.C_STYLE
        else:
            # try to guess a pound-style
            style = re.search(
                r"#(?:.*)@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@(?:.*)#\n(.*)", contents,
                re.MULTILINE | re.DOTALL)
            if style:
                self.style = Style.POUND_STYLE
            else:
                # no style determination possible
                style = re.search(
                    r'@LICENSE_HEADER_START@(.+)@LICENSE_HEADER_END@', contents,
                    re.MULTILINE | re.DOTALL)
        if style:
            self.license = re.sub(
                r'^. ', '', style[1], flags=re.MULTILINE).strip()
            self.remainder = style[2].strip()
        else:
            self.license = None
            self.remainder = contents.strip()
        pass


class Tool:
    def __init__(self, default_license: License, default_author: Author):
        self.default_license = default_license
        self.default_author = default_author

    def bump(self, filename: pathlib.PurePath) -> str:
        parsed = ParsedHeader(filename)
        return str(parsed)

    def generate(self, filename: str, style: Style) -> str:
        return self.default_license.render(filename=filename, authors=[self.default_author], style=style)
