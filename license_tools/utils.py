# utils.py
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
Various utilities
"""

import datetime
import os
import logging
import enum
import functools
import re


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

    @staticmethod
    def parse_git_date(git_date: str) -> datetime.datetime:
        """
        Returns a datetime parsed from a git date string
        as documented at https://git-scm.com/docs/git-commit/2.24.0#_date_formats
        """
        # Git internal format
        try:
            if git_date.startswith('@'):
                unix_timestamp, tz_offset = git_date[1:].split(' ', maxsplit=1)
                unix_timestamp = int(unix_timestamp)
                timezone = datetime.timezone(datetime.datetime.strptime(tz_offset, '%z').utcoffset())
                return datetime.datetime.fromtimestamp(unix_timestamp, tz=timezone)
        except:  # pylint: disable=bare-except
            pass

        # RFC 2822
        try:
            from email.utils import parsedate_to_datetime  # pylint: disable=import-outside-toplevel
            author_date = parsedate_to_datetime(git_date)
            if author_date:
                return author_date
        except:  # pylint: disable=bare-except
            pass

        # ISO 8601
        try:
            return datetime.datetime.fromisoformat(git_date)
        except:  # pylint: disable=bare-except
            pass

        # plain formats
        for format in ['%Y.%m.%d', '%m/%d/%Y', '%d.%m.%Y']:
            try:
                return datetime.datetime.strptime(git_date, format)
            except:  # pylint: disable=bare-except
                pass

        raise RuntimeError(f"Not a supported git date format: {git_date}")


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
