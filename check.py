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
# <dmars+github@protonmail.com>
#------------------------------------------------------------------------------

"""Check existence of files in unencrypted and encrypted directory
based on the register list. Register is a schema in inventory.sqlite
that contains mapping between encrypted and unencrypted files.

Reports discrepancies unless switch is specified to clean up.
"""

import sys
import os
import argparse
import getpass
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'lib'))

from direncrypt.consistency import ConsistencyCheck


if __name__ == "__main__":

    database = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'inventory.sqlite')

    parser = argparse.ArgumentParser(
            'Check/fix consistency between unencrypted and encrypted files')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--clean',
            action='store_true',
            help='File does not exist, delete entry from register')
    group.add_argument('-r', '--resync',
            action='store_true',
            help='Effectively decrypt existing encrypted file to plaindir')

    args = parser.parse_args()

    c = ConsistencyCheck(database)
    c.check()

    if args.clean:
        c.loop_through(clean=True)
    elif args.resync:
        passphrase = getpass.getpass('Passphrase: ')
        c.set_passphrase(passphrase)
        c.loop_through(resync=True)
    else:
        c.loop_through()
