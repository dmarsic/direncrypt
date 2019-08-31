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
from direncrypt.consistency import ConsistencyCheck

saved_params = {
    'last_timestamp': 1234567890,
    'plaindir'      : 'param_plaindir',
    'securedir'     : 'param_securedir',
    'public_id'     : 'param_public_id',
    'gpg_keyring'   : 'param_gpg_keyring',
    'gpg_homedir'   : 'param_gpg_homedir',
    'gpg_binary'    : 'param_gpg_binary'
}

@patch('direncrypt.consistency.Inventory')
def test_set_passphrase(Inventory):
    """Test if passphrase is set correctly."""
    c = ConsistencyCheck('test_database')
    c.set_passphrase('passphr4s3')
    eq_(c.passphrase, 'passphr4s3')

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

    ok_(c.registered_files['unenc_1']['unencrypted_file_check'])
    ok_(c.registered_files['unenc_1']['encrypted_file_check'])
    assert c.registered_files['unenc_2']['unencrypted_file_check']==False
    ok_(c.registered_files['unenc_2']['encrypted_file_check'])

@patch('direncrypt.consistency.Inventory')
def test_clean_registry(Inventory):
    """Test that clean_record is called with filename."""
    c = ConsistencyCheck('test_database')
    c.clean_registry('test_file')

    eq_(Inventory().__enter__().clean_record.call_args[0][0], 'test_file')

@patch('direncrypt.consistency.Inventory')
@patch('direncrypt.consistency.DirEncryption')
@patch('direncrypt.consistency.FileOps.delete_file')
def test_loop_through(delete_file, DirEncryption, Inventory):
    """Check number of function executions in the workflow.

    Test clean function and resync function. Mock calls are reset
    between tests."""
    c = ConsistencyCheck('test_database')
    c.clean_registry = MagicMock()
    c.registered_files = {
        'unenc_1': {
            'unencrypted_file'       : 'unenc_1',
            'encrypted_file'         : 'enc_1',
            'unencrypted_file_check' : False,
            'encrypted_file_check'   : True
        },
        'unenc_2': {
            'unencrypted_file'       : 'unenc_2',
            'encrypted_file'         : 'enc_2',
            'unencrypted_file_check' : True,
            'encrypted_file_check'   : False
        }
    }

    c.loop_through(clean=True)
    eq_(delete_file.call_count, 2)
    eq_(c.clean_registry.call_count, 2)
    eq_(DirEncryption.call_count, 0)

    delete_file.reset_mock()
    c.clean_registry.reset_mock()
    DirEncryption.reset_mock()

    c.set_passphrase('test_pass')
    c.loop_through(resync=True)
    eq_(delete_file.call_count, 0)
    eq_(c.clean_registry.call_count, 0)
    eq_(DirEncryption.call_count, 1)

@patch('direncrypt.consistency.Inventory')
@patch('direncrypt.consistency.FileOps.delete_file')
@patch('direncrypt.consistency.os.walk')
def test_delete_orphans_encrypted_files_with_files(walk, delete_file, inv):
    
    c = ConsistencyCheck('test_database')
    
    walk.return_value = [
        (['plaindir'], ['subdir_1'], ['unenc_1', 'unenc_2', 'unenc_3']),
        (os.path.join('plaindir', 'subdir_1'), [], ['unenc_4'])
    ]    
    inv().__enter__().exists_encrypted_file.return_value = False
    c.delete_orphans_encrypted_files()
    eq_(delete_file.call_count, 4)
    inv().__exit__()
    
@patch('direncrypt.consistency.Inventory')
@patch('direncrypt.consistency.FileOps.delete_file')
@patch('direncrypt.consistency.os.walk')
def test_delete_orphans_encrypted_files_no_files(walk, delete_file, inv):
    
    c = ConsistencyCheck('test_database')
    
    walk.return_value = [
        (['plaindir'], ['subdir_1'], ['unenc_1', 'unenc_2', 'unenc_3']),
        (os.path.join('plaindir', 'subdir_1'), [], ['unenc_4'])
    ]    
    
    inv().__enter__().exists_encrypted_file.return_value = True
    c.delete_orphans_encrypted_files()
    eq_(delete_file.call_count, 0)
    