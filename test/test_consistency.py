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
from direncrypt.consistency import ConsistencyCheck

@patch('direncrypt.consistency.Inventory')
@patch('direncrypt.consistency.os.path.expanduser')
@patch('direncrypt.consistency.os.path.exists')
def test_check(exists, expanduser, Inventory):
    """Test flags for unencrypted and encrypted files.

    The flags are set based on the existence of files on the filesystem
    and the existence is mocked in this function.
    """
    Inventory().__enter__().read_parameters.return_value = {
        'plaindir': 'test_plaindir',
        'securedir': 'test_securedir'
    }

    Inventory().__enter__().read_register.return_value = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1'
        },
        'unenc_2': {
            'unencrypted_file': 'unenc_2',
            'encrypted_file': 'uuid-2'
        }
    }

    expanduser.side_effect = [
        os.path.join('test_plaindir', 'unenc_1'),
        os.path.join('test_securedir', 'uuid-1'),
        os.path.join('test_plaindir', 'unenc_2'),
        os.path.join('test_securedir', 'uuid-2')
    ]

    exists.side_effect = [True, True, False, True]

    c = ConsistencyCheck('test_database')
    c.check()

    ok_(c.fileset['unenc_1']['unencrypted_file_check'])
    ok_(c.fileset['unenc_1']['encrypted_file_check'])
    ok_(not c.fileset['unenc_2']['unencrypted_file_check'])
    ok_(c.fileset['unenc_2']['encrypted_file_check'])
