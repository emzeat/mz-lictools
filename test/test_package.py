# test.py
#
# Copyright (c) 2021 - 2025 Marius Zwicker
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

from asyncio import subprocess
import os
import pathlib
import shutil
import subprocess
import tempfile
import textwrap
import unittest

BASE = pathlib.Path(__file__).resolve().absolute().parent.parent


class TestPackage(unittest.TestCase):

    def _prepare_repo(self, commit: pathlib.Path, config: pathlib.Path):
        # override any external input to the git config so we truly
        # use our expected config to ensure tests cannot fail
        os.putenv('GIT_CONFIG_COUNT', '0')

        wkdir = tempfile.TemporaryDirectory(suffix='lictools')
        try:
            cwd = pathlib.Path(wkdir.name)
            subprocess.check_call('git init --initial-branch=master', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            (cwd / ".gitignore").write_text("")
            subprocess.check_call('git add .gitignore', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('git commit -a -m "Prepare Repo"', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('git config --local user.name "Lictools Unittest"',
                                  cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('git config --local user.email "lictools@unittest.local"',
                                  cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call(f'git am {commit}', cwd=cwd, shell=True, stdout=subprocess.DEVNULL)
            (cwd / '.license-tools-config.json').write_text(config.read_text())
            return wkdir
        except:
            wkdir.cleanup()
            raise

    def _diff_repo(self, repo: pathlib.Path, expected: pathlib.Path):
        diff = subprocess.check_output('git diff', cwd=repo, shell=True, encoding='utf-8')
        try:
            with open(expected, 'r') as raw:
                self.assertEqual(raw.read(), diff)
        except:
            with open(expected, 'w') as raw:
                raw.write(diff)
            raise

    def test_bad_config(self):
        with self._prepare_repo(BASE / 'test/package/noglob_package_bad_license.patch',
                                BASE / 'test/package/noglob_package_bad_license.patch') as repo:
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_no_config(self):
        with self._prepare_repo(BASE / 'test/package/noglob_package_bad_license.patch',
                                BASE / 'test/package/noglob_package_bad_license.patch') as repo:
            (pathlib.Path(repo) / '.license-tools-config.json').unlink()
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_bad_license(self):
        with self._prepare_repo(BASE / 'test/package/noglob_package_bad_license.patch',
                                BASE / 'test/package/noglob_package_bad_license.json') as repo:
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_from_git_no_repo(self):
        with self._prepare_repo(BASE / 'test/package/noglob_package_from_git_no_repo.patch',
                                BASE / 'test/package/noglob_package_from_git_no_repo.json') as repo:
            shutil.rmtree(pathlib.Path(repo) / '.git')
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)

    def test_new_author(self):
        with self._prepare_repo(BASE / 'test/package/noglob_package_from_git_new_author.patch',
                                BASE / 'test/package/noglob_package_from_git_new_author.json') as repo:
            code = pathlib.Path(repo) / 'code.cpp'
            code.write_text(code.read_text() + "\ninline void unused(){}\n\n")
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package/noglob_package_from_git_new_author.diff')

    def test_commit_amend(self):
        with self._prepare_repo(BASE / 'test/package/noglob_package_commit_amend.patch',
                                BASE / 'test/package/noglob_package_commit_amend.json') as repo:
            # trigger a change
            code = pathlib.Path(repo) / 'code.cpp'
            code.write_text(code.read_text() + "\ninline void unused(){}\n")
            # enable pre-commit
            precommit = pathlib.Path(repo) / '.pre-commit-config.yaml'
            precommit.write_text(textwrap.dedent(f'''
                                 repos:
                                 -   repo: local
                                     hooks:
                                     - id: license-tools
                                       name: Check license headers
                                       entry: {BASE}/lictool
                                       language: python
                                       types: [text]
                                       additional_dependencies: ['jinja2']
                                       verbose: true
                                '''))
            subprocess.check_call(['pre-commit', 'install'], cwd=repo)
            # amend the change, pre-commit should run lictool and continue as there is no changes
            subprocess.check_call(['git', 'add', '.pre-commit-config.yaml'], cwd=repo)
            subprocess.check_call(['git', 'commit', '--amend', '-a', '-m', 'Amended Message'], cwd=repo)
            self._diff_repo(repo, BASE / 'test/package/noglob_package_commit_amend.diff')
            # running lictool directly should not register changes either
            subprocess.check_call(f'{BASE}/lictool', cwd=repo)
            self._diff_repo(repo, BASE / 'test/package/noglob_package_commit_amend.diff')


for file in BASE.glob('test/package/package_*.patch'):
    def create_test_case():
        patch = file
        json = patch.with_suffix('.json')
        diff = patch.with_suffix('.diff')

        def test_glob_case(self):
            with self._prepare_repo(patch, json) as repo:
                subprocess.check_call(f'{BASE}/lictool', cwd=repo)
                self._diff_repo(repo, diff)
        return test_glob_case
    setattr(TestPackage, f'test_{file.stem.replace("package_", "")}', create_test_case())
