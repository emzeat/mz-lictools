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

import unittest
import license_tools


class TestDateUtils(unittest.TestCase):

    def test_git_date_format(self):
        EXPRESSIONS = [
            ('Thu, 07 Apr 2005 22:13:13 +0200', 2005, 4, 7),  # RFC 2822
            ('2005-04-07T22:13:13', 2005, 4, 7),  # ISO 8601
            ('1998.02.01', 1998, 2, 1),
            ('01/02/1987', 1987, 1, 2),
            ('@1453791344 +0100', 2016, 1, 26),  # git internal format
        ]
        for expression, year, month, day in EXPRESSIONS:
            date = license_tools.DateUtils.parse_git_date(expression)
            self.assertEqual(date.year, year)
            self.assertEqual(date.month, month)
            self.assertEqual(date.day, day)
