#------------------------------------------------------------------------------
# direncrypt - Sync contents between encrypted and decrypted directories
# Copyright (C) 2015-2019  Domagoj Marsic
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

import os
import nose
from nose.tools import *
from mock import patch, call
from direncrypt.database_builder import DatabaseBuilder


@patch('direncrypt.database_builder.glob')
@patch('direncrypt.database_builder.sqlite3')
@patch('direncrypt.database_builder.open')
def test_build(open, sqlite3, glob):
    """Test that database is built with sql files applied in sorted order."""
    database_file = 'database.sqlite'
    file_content = {
        'file_c': 'content_c',
        'file_a': 'content_a',
        'file_b': 'content_b'
    }

    glob.glob.return_value = ['file_c', 'file_a', 'file_b']
    open.return_value.__enter__.return_value.read.side_effect = [
        file_content[key] for key in sorted(file_content.keys())
    ]

    builder = DatabaseBuilder(database_file)
    builder.build()

    calls = [call('content_a'), call('content_b'), call('content_c')]
    sqlite3.connect.return_value.executescript.assert_has_calls(calls, any_order=False)
