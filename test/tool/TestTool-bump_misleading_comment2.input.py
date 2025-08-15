#
# TestTool-bump_misleading_comment2.input.py
#
# Copyright (c) 2021 Test Guy
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

def main():
    pass
    # note: This is not a Copyright for 1 but only using the word :)

    /* some artifical text to trigger our fault
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
    */
