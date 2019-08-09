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

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'lib'))


import nose
from nose.tools import *
from mock import MagicMock, patch
from direncrypt.inventory import Inventory

@patch('direncrypt.inventory.sqlite3')
def test_inventory_enter(sqlite3):
    with Inventory('test_database') as i:
        ok_(i.cursor)

@patch('direncrypt.inventory.sqlite3.connect')
def test_read_parameters(connect):

    connect().cursor().execute.side_effect = [
        [
            ('param-key-1', 'param-value-1'),
            ('param-key-2', 'param-value-2')
        ],
        [
            ('state-key-1', 'state-value-1')
        ]
    ]

    with Inventory('test_database') as inv:
        params = inv.read_parameters()

    eq_(len(params), 3)
    for k in ['param-key-1', 'param-key-2', 'state-key-1']:
        ok_(k in params.keys())
    eq_(params['state-key-1'], 'state-value-1')

@patch('direncrypt.inventory.sqlite3.connect')
def test_read_register(connect):

    connect().cursor().execute.return_value = [
        ('unenc_1', 'uuid-1', 'public_id_1'),
        ('unenc_2', 'uuid-2', 'public_id_2'),
        ('unenc_3', 'uuid-3', 'public_id_3')
    ]

    with Inventory('test_database') as inv:
        rows = inv.read_register()

    eq_(len(rows), 3)
    for f in ['unenc_1', 'unenc_2', 'unenc_3']:
        ok_(f in rows.keys())
    eq_(rows['unenc_2']['unencrypted_file'], 'unenc_2')
    eq_(rows['unenc_2']['encrypted_file'], 'uuid-2')
    eq_(rows['unenc_2']['public_id'], 'public_id_2')


@patch('direncrypt.inventory.sqlite3.connect')
def test_register(connect):

    with Inventory('test_database') as inv:
        inv.register('plain', 'encrypted', 'public_id')

        eq_(inv.cursor.execute.call_count, 1)
        eq_(inv.cursor.execute.call_args[0][1],
            ('plain', 'encrypted', 'public_id'))

@patch('direncrypt.inventory.sqlite3.connect')
def test_update_parameters(connect):

    with Inventory('test_database') as inv:
        inv.update_parameters('key_1', 'value_1')

        eq_(inv.cursor.execute.call_count, 1)
        eq_(inv.cursor.execute.call_args[0][1], ('value_1', 'key_1'))
