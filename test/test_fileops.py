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

import nose
from nose.tools import *
from mock import patch
from direncrypt.fileops import FileOps


@patch('direncrypt.fileops.os.unlink')
def test_delete_file(unlink):
    """File deleted successfully."""
    r = FileOps.delete_file('test_dir', 'test_file')
    assert r == True

@patch('direncrypt.fileops.os.unlink')
def test_delete_file__os_error(unlink):
    """Error while deleting file."""
    unlink.side_effect = OSError('Boom!')
    r = FileOps.delete_file('test_dir', 'test_file')
    assert r == False

@patch('direncrypt.fileops.os.symlink')
def test_create_symlink(symlink):
    """Symlink created successfully."""
    r = FileOps.create_symlink('test_dir', 'test_name', 'test_target')
    assert r == True

@patch('direncrypt.fileops.os.symlink')
def test_create_symlink_os_error(symlink):
    """Exception while creating symlink."""
    symlink.side_effect = OSError('Boom!')
    r = FileOps.create_symlink('test_dir', 'test_name', 'test_target')
    assert r == False

@patch('direncrypt.fileops.os.mkdir')
def test_create_directory(mkdir):
    """Directory created successfully."""
    r = FileOps.create_directory('test_dir', 'test_name')
    assert r == True

@patch('direncrypt.fileops.os.mkdir')
def test_create_directory_os_error(mkdir):
    """Error while creating directory."""
    mkdir.side_effect = OSError('Boom!')
    r = FileOps.create_directory('test_dir', 'test_name')
    assert r == False
