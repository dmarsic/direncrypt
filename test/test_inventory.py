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
def test_read_all_register(connect):

    connect().cursor().execute.return_value = [
        ('unenc_1', 'uuid-1', 'public_id_1', 0, ''),
        ('unenc_2', '', '', 1, 'target_2'),
        ('unenc_3', '', '', 1, 'target_3'),
        ('unenc_4', '', '', 0, '')
    ]

    with Inventory('test_database') as inv:
        rows = inv.read_all_register()

    eq_(len(rows), 4)
    for f in ['unenc_1', 'unenc_2', 'unenc_3', 'unenc_4']:
        ok_(f in rows.keys())
    eq_(rows['unenc_2']['unencrypted_file'], 'unenc_2')
    eq_(rows['unenc_2']['encrypted_file'], '')
    eq_(rows['unenc_2']['public_id'], '')
    eq_(rows['unenc_2']['is_link'], 1)
    eq_(rows['unenc_2']['target'], 'target_2')

@patch('direncrypt.inventory.sqlite3.connect')
def test_read_registered_files(connect):

    connect().cursor().execute.return_value = [
        ('unenc_1', 'uuid-1', 'public_id_1', 0, ''),
        ('unenc_2', 'uuid-2', 'public_id_2', 0, '')
    ]

    with Inventory('test_database') as inv:
        rows = inv.read_registered_files()

    eq_(len(rows), 2)
    for f in ['unenc_1', 'unenc_2']:
        ok_(f in rows.keys())
    eq_(rows['unenc_2']['unencrypted_file'], 'unenc_2')
    eq_(rows['unenc_2']['encrypted_file'], 'uuid-2')
    eq_(rows['unenc_2']['public_id'], 'public_id_2')
    eq_(rows['unenc_2']['is_link'], 0)
    eq_(rows['unenc_2']['target'], '')
    
@patch('direncrypt.inventory.sqlite3.connect')
def test_read_registered_links(connect):

    connect().cursor().execute.return_value = [
        ('unenc_1', '', '', 1, 'target_1'),
        ('unenc_2', '', '', 1, 'target_2')
    ]

    with Inventory('test_database') as inv:
        rows = inv.read_registered_links()

    eq_(len(rows), 2)
    for f in ['unenc_1', 'unenc_2']:
        ok_(f in rows.keys())
    eq_(rows['unenc_2']['unencrypted_file'], 'unenc_2')
    eq_(rows['unenc_2']['encrypted_file'], '')
    eq_(rows['unenc_2']['public_id'], '')
    eq_(rows['unenc_2']['is_link'], 1)
    eq_(rows['unenc_2']['target'], 'target_2')
    
@patch('direncrypt.inventory.sqlite3.connect')
def test_read_registered_dirs(connect):

    connect().cursor().execute.return_value = [
        ('unenc_1', '', '', 0, ''),
        ('unenc_2', '', '', 0, '')
    ]

    with Inventory('test_database') as inv:
        rows = inv.read_registered_links()

    eq_(len(rows), 2)
    for f in ['unenc_1', 'unenc_2']:
        ok_(f in rows.keys())
    eq_(rows['unenc_2']['unencrypted_file'], 'unenc_2')
    eq_(rows['unenc_2']['encrypted_file'], '')
    eq_(rows['unenc_2']['public_id'], '')
    eq_(rows['unenc_2']['is_link'], 0)
    eq_(rows['unenc_2']['target'], '')

@patch('direncrypt.inventory.sqlite3.connect')
def test_register(connect):

    with Inventory('test_database') as inv:
        inv.register('plain', 'encrypted', 'public_id', 1, 'target')

        eq_(inv.cursor.execute.call_count, 1)
        eq_(inv.cursor.execute.call_args[0][1],
            ('plain', 'encrypted', 'public_id', 1, 'target'))

@patch('direncrypt.inventory.sqlite3.connect')
def test_update_parameters(connect):

    with Inventory('test_database') as inv:
        inv.update_parameters('key_1', 'value_1')

        eq_(inv.cursor.execute.call_count, 1)
        eq_(inv.cursor.execute.call_args[0][1], ('value_1', 'key_1'))
        
@patch('direncrypt.inventory.sqlite3.connect')
def test_exists_encrypted_file(connect):

    with Inventory('test_database') as inv:
        r = inv.exists_encrypted_file('filename')

        assert inv.cursor.execute.call_count==1
        assert inv.cursor.execute.call_args[0][1]==('filename',)
        assert r==True or r==False
