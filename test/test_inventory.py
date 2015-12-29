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

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'lib'))


import nose
from nose.tools import *
from mock import MagicMock, patch
from direncrypt.inventory import Inventory

@patch('direncrypt.inventory.sqlite3')
def test_inventory(sqlite3):
    sqlite3.connect.return_value.cursor.return_value.execute.return_value = [1]

    with Inventory('test_database') as i:
        print i
        for row in i.execute('SELECT 1'):
            eq_(row, 1)
