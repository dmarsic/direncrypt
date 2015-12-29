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


import os
import nose
from nose.tools import *
from mock import MagicMock, patch
from direncrypt.direncryption import DirEncryption

saved_params = {
    'last_timestamp': 1234567890,
    'plaindir'      : 'param_plaindir',
    'securedir'     : 'param_securedir',
    'public_id'     : 'param_public_id',
    'gpg_keyring'   : 'param_gpg_keyring',
    'gpg_homedir'   : 'param_gpg_homedir',
    'gpg_binary'    : 'param_gpg_binary'
}

test_args = MagicMock()
test_args.verbose = None
test_args.plaindir = None
test_args.securedir = None
test_args.public_id = None
test_args.gpg_keyring = None
test_args.gpg_homedir = None
test_args.gpg_binary = None


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_set_parameters__from_param(expanduser, read_params, Inventory, GPGOps):


    read_params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de1 = DirEncryption(test_args)
    eq_(de1.verbose, False)
    eq_(de1.last_timestamp, saved_params['last_timestamp'])
    eq_(de1.plaindir, saved_params['plaindir'])
    eq_(de1.securedir, saved_params['securedir'])
    eq_(de1.public_id, saved_params['public_id'])
    eq_(de1.gpg_keyring, saved_params['gpg_keyring'])
    eq_(de1.gpg_homedir, saved_params['gpg_homedir'])
    eq_(de1.gpg_binary, saved_params['gpg_binary'])


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_set_parameters__from_args(expanduser, read_params, Inventory, GPGOps):

    read_params.return_value = saved_params

    args = MagicMock()
    args.verbose = True
    args.plaindir = 'runtime_plaindir'
    args.securedir = 'runtime_securedir'
    args.public_id = 'runtime_public_id'
    args.gpg_keyring = 'runtime_gpg_keyring'
    args.gpg_homedir = 'runtime_gpg_homedir'
    args.gpg_binary = 'runtime_gpg_binary'

    expanduser.side_effect = [
        args.plaindir,
        args.securedir,
        args.gpg_homedir,
        args.gpg_binary,
        args.plaindir,
        args.securedir,
        args.gpg_homedir,
        args.gpg_binary
    ]

    de = DirEncryption(args)
    eq_(de.verbose, True)
    eq_(de.last_timestamp, saved_params['last_timestamp'])
    eq_(de.plaindir, args.plaindir)
    eq_(de.securedir, args.securedir)
    eq_(de.public_id, args.public_id)
    eq_(de.gpg_keyring, args.gpg_keyring)
    eq_(de.gpg_homedir, args.gpg_homedir)
    eq_(de.gpg_binary, args.gpg_binary)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.register')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_encrypt(expanduser, params, register, Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)
    de.encrypt('plainfile', 'securefile')
    eq_(register.call_count, 1)
    de.gpg.encrypt.assert_called_once_with(
        os.path.join(saved_params['plaindir'], 'plainfile'),
        os.path.join(saved_params['securedir'], 'securefile')
    )


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.read_register')
@patch('direncrypt.direncryption.DirEncryption.find_unencrypted_files')
@patch('direncrypt.direncryption.DirEncryption.encrypt')
@patch('direncrypt.direncryption.DirEncryption.update_last_timestamp')
def test_encrypt_all__no_files(update_ts, encrypt, find, read_reg,
                               expanduser, params, Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    find.return_value = {}

    de = DirEncryption(test_args)
    de.encrypt_all()

    eq_(read_reg.call_count, 1)
    eq_(encrypt.call_count, 0)
    eq_(update_ts.call_count, 1)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.read_register')
@patch('direncrypt.direncryption.DirEncryption.find_unencrypted_files')
@patch('direncrypt.direncryption.DirEncryption.encrypt')
@patch('direncrypt.direncryption.DirEncryption.update_last_timestamp')
def test_encrypt_all(update_ts, encrypt, find, read_reg,
                     expanduser, params, Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    find.return_value = {
        'test_path_1': {'modified_time': 1234},
        'test_path_2': {'modified_time': 1337},
        'test_path_3': {'modified_time': 1414}
    }

    de = DirEncryption(test_args)
    de.encrypt_all()

    eq_(read_reg.call_count, 1)
    eq_(encrypt.call_count, 3)
    eq_(encrypt.call_args_list[0][0][0], 'test_path_1')
    eq_(encrypt.call_args_list[1][0][0], 'test_path_2')
    eq_(encrypt.call_args_list[2][0][0], 'test_path_3')
    eq_(update_ts.call_count, 1)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_decrypt(expanduser, params, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)
    de.decrypt('test_enc_file', 'test_plain_file', 'trustno1')

    de.gpg.decrypt.assert_called_once_with(
        os.path.join(saved_params['securedir'], 'test_enc_file'),
        os.path.join(saved_params['plaindir'], 'test_plain_file'),
        'trustno1'
    )


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.read_register')
@patch('direncrypt.direncryption.DirEncryption.decrypt')
def test_decrypt_all__no_files(decrypt, read_reg, expanduser, params,
                               Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    read_reg.return_value = {}

    de = DirEncryption(test_args)
    de.decrypt_all('trustno1')

    eq_(de.decrypt.call_count, 0)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.read_register')
@patch('direncrypt.direncryption.DirEncryption.decrypt')
def test_decrypt_all(decrypt, read_reg, expanduser, params, Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    read_reg.return_value = {
        'unenc_file_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id']
        },
        'unenc_file_2': {
            'unencrypted_file': 'unenc_2',
            'encrypted_file': 'uuid-2',
            'public_id': saved_params['public_id']
        },
        'unenc_file_3': {
            'unencrypted_file': 'unenc_3',
            'encrypted_file': 'uuid-3',
            'public_id': 'some_other_id'
        }

    }

    de = DirEncryption(test_args)
    de.decrypt_all('trustno1')

    eq_(de.decrypt.call_count, 2)
    eq_(de.decrypt.call_args_list[0][0], ('uuid-1', 'unenc_1', 'trustno1'))
    eq_(de.decrypt.call_args_list[1][0], ('uuid-2', 'unenc_2', 'trustno1'))


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_read_register(expanduser, params, Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)

    Inventory().__enter__().execute.return_value = [
        ('unenc_1', 'uuid-1', saved_params['public_id']),
        ('unenc_2', 'uuid-2', saved_params['public_id']),
        ('unenc_3', 'uuid-3', 'other_public_id')
    ]

    with Inventory() as inv:
        rows = de.read_register(inv)

        eq_(len(rows), 3)
        for f in ['unenc_1', 'unenc_2', 'unenc_3']:
            ok_(f in rows.keys())
        eq_(rows['unenc_2']['unencrypted_file'], 'unenc_2')
        eq_(rows['unenc_2']['encrypted_file'], 'uuid-2')
        eq_(rows['unenc_2']['public_id'], saved_params['public_id'])


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.walk')
def test_find_unencrypted_files__empty_dir(walk, expanduser, params,
                                           Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    register = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id']
        }
    }

    walk.return_value = []

    de = DirEncryption(test_args)
    files = de.find_unencrypted_files(register)

    eq_(files, {})


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.walk')
@patch('direncrypt.direncryption.os.stat')
def test_find_unencrypted_files(stat, walk, expanduser, params,
                                Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    register = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id']
        }
    }

    walk.return_value = [
        (saved_params['plaindir'], ['subdir_1'], ['unenc_1', 'unenc_2']),
        (os.path.join(saved_params['plaindir'], 'subdir_1'), [], ['unenc_3'])
    ]

    stat = MagicMock()
    stat.st_mtime = 1400

    de = DirEncryption(test_args)
    files = de.find_unencrypted_files(register)

    eq_(len(files), 2)
    ok_('unenc_2' in files.keys())
    ok_(os.path.join('subdir_1', 'unenc_3') in files.keys())


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.read_parameters')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_register(expanduser, params, Inventory, GPGOps):

    params.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)

    with Inventory() as inv:
        de.register(inv, 'plain', 'encrypted')

    eq_(Inventory().__enter__().execute.call_count, 1)
    eq_(Inventory().__enter__().execute.call_args[0][1],
        ('plain', 'encrypted', saved_params['public_id']))
