#!/usr/bin/env python

#------------------------------------------------------------------------------
# direncrypt - Sync contents between encrypted and decrypted directories
# Copyright (C) 2015  Domagoj Marsic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact:
# https://github.com/dmarsic
# <dmars@protonmail.com> or <domagoj.marsic@gmail.com>
#------------------------------------------------------------------------------

"""Check existence of files in unencrypted and encrypted directory
based on the register list. Register is a schema in inventory.sqlite
that contains mapping between encrypted and unencrypted files.

Reports discrepancies unless switch is specified to clean up."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'lib'))

from direncrypt.consistency import ConsistencyCheck

if __name__ == "__main__":

    database = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'inventory.sqlite')

    c = ConsistencyCheck(database)
    c.check()
    c.print_formatted()
