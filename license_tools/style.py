# style.py
#
# Copyright (c) 2012 - 2025 Marius Zwicker
# Copyright (c) 2025 François Bastien
# Copyright (c) 2025 Alberto Chiusole
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
Handling of different comment styles
"""

import enum
from collections import namedtuple


class Style(enum.Enum):
    """Enumerates the different known comment styles"""
    UNKNOWN = 1
    C_STYLE = 2
    POUND_STYLE = 3
    DOCSTRING_STYLE = 4
    XML_STYLE = 5
    BATCH_STYLE = 6
    SLASH_STYLE = 7
    DASH_STYLE = 8
    TRIPLE_SLASH_STYLE = 9
    GO_TEXT_TEMPLATE_STYLE = 10

    @classmethod
    def set_overrides(cls, suffix_overrides=None):
        """Assigns custom mappings of file suffix to style"""
        setattr(cls, '__suffix_overrides', suffix_overrides)

    @classmethod
    def from_suffix(cls, ext):
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
            '.lua': Style.DASH_STYLE,
            '.rs': Style.SLASH_STYLE,
            '.toml': Style.POUND_STYLE,
            '.tpl': Style.GO_TEXT_TEMPLATE_STYLE
        }
        suffix_overrides = getattr(cls, '__suffix_overrides', None)
        if suffix_overrides and ext in suffix_overrides:  # pylint: disable=unsupported-membership-test
            return Style[suffix_overrides[ext]]  # pylint: disable=unsubscriptable-object
        return mapping.get(ext, None) or mapping.get(ext.lower(), Style.UNKNOWN)

    @staticmethod
    def from_name(name):
        """Tries to determine the style based on a file name"""
        mapping = {
            'CMakeLists.txt': Style.POUND_STYLE,
            'requirements.txt': Style.POUND_STYLE,
            'Cargo.lock': Style.POUND_STYLE,
            'Cargo.toml': Style.POUND_STYLE
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
                r"#(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(?P<body>[^#](.*)|$)"),
            (Style.DOCSTRING_STYLE,
                r"\"\"\"\r?\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\r?\n\"\"\"(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"\"\"\"\r?\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)\"\"\"\r?\n(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"#(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)# +@LICENSE_HEADER_END@(?:.*?)#\r?\n(?P<body>.*)"),
            (Style.DOCSTRING_STYLE,
                r"#(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(?P<body>[^#](.*)|$)"),
            (Style.XML_STYLE,
                r"<!--\r?\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\r?\n-->(?P<body>.*)"),
            (Style.XML_STYLE,
                r"<!--\r?\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)-->\r?\n(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"REM(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)REM\r?\n(?!REM)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"REM(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(?P<body>(?!REM)(.*)|$)"),
            (Style.BATCH_STYLE,
                r"::(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)::\r?\n(?!::)(?P<body>.*)"),
            (Style.BATCH_STYLE,
                r"::(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(::)?\r?\n(?!::)(?P<body>.*)"),
            (Style.SLASH_STYLE,
                r"//(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)// +@LICENSE_HEADER_END@(?:.*?)//\r?\n(?P<body>.*)"),
            (Style.TRIPLE_SLASH_STYLE,
                r"///(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(?P<body>[^/](.*)|$)"),
            (Style.SLASH_STYLE,
                r"//(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(?P<body>[^/](.*)|$)"),
            (Style.DASH_STYLE,
                r"--(?P<authors>.+?)All rights reserved\.(?P<license>.+?)^(?P<body>[^-](.*)|$)"),
            (Style.GO_TEXT_TEMPLATE_STYLE,
                r"\{\{/\*\r?\n(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?:.*?)\r?\n\*/\}\}(?P<body>.*)"),
            (Style.GO_TEXT_TEMPLATE_STYLE,
                r"\{\{/\*\r?\n(?P<authors>.+?)All rights reserved\.(?P<license>.+?)\*/\}\}\r?\n(?P<body>.*)"),
            (Style.UNKNOWN,
                r"(?P<authors>.+?)@LICENSE_HEADER_START@(?P<license>.+?)@LICENSE_HEADER_END@(?P<body>.*)"),
        ]
        if style is None:
            style = Style.UNKNOWN
        if style == Style.UNKNOWN:
            # slow path, we have to try all of the patterns
            return style_patterns
        # fast path, move the expected style to the front
        return sorted(style_patterns, key=lambda s: s[0] != style)

    @staticmethod
    def declarations():
        """
        Returns a list of document declarations retained at the first line

        Each entry is a pair of matching regex and additional flags required
        """
        return [
            # unicode bom marker
            (r'\uFEFF', 0),
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
            return Decorator(None, '#', None, r' ?(?:#) ?')
        if style == Style.DOCSTRING_STYLE:
            # the pattern will help to translate any #-style and """-style docstrings
            return Decorator(None, '#', None, r' ?(?:#) ?')
        if style == Style.XML_STYLE:
            return Decorator('<!--', '', '-->', None)
        if style == Style.BATCH_STYLE:
            return Decorator(None, 'REM', None, r' ?(?:REM|::) ?')
        if style == Style.SLASH_STYLE:
            return Decorator(None, '//', None, r'^ ?(?://) ?')
        if style == Style.DASH_STYLE:
            return Decorator(None, '--', None, r' ?(?:--) ?')
        if style == Style.TRIPLE_SLASH_STYLE:
            return Decorator(None, '///', None, r' ?(?:///) ?')
        if style == Style.GO_TEXT_TEMPLATE_STYLE:
            return Decorator('{{/*', '', '*/}}', None)
        return Decorator('', '', '', None)
