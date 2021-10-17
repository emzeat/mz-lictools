#
# __main__.py
#
# Copyright (c) 2021 Marius Zwicker
# All rights reserved.
#
# @LICENSE_HEADER_START@
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# @LICENSE_HEADER_END@
#

import license_tools
import sys

if __name__ == "__main__":
    try:
        license_tools.main()
    except Exception as e:
        print(e)
        sys.exit(1)
