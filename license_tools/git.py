# git.py
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
Abstraction of operations on a git repo
"""

import functools
import logging
import pathlib
import subprocess

from .header import Author

CW_DIR = pathlib.Path.cwd()


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
