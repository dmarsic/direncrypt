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

import os
import nose
from nose.tools import *
from mock import Mock, MagicMock, patch
from direncrypt.direncryption import DirEncryption

saved_params = {
    'last_timestamp': 1234567890,
    'plaindir'      : 'param_plaindir',
    'securedir'     : 'param_securedir',
    'restoredir'    : 'param_restoredir',
    'public_id'     : 'param_public_id',
    'gpg_keyring'   : 'param_gpg_keyring',
    'gpg_homedir'   : 'param_gpg_homedir',
    'gpg_binary'    : 'param_gpg_binary'
}

test_args = MagicMock()
test_args.verbose = None
test_args.plaindir = None
test_args.securedir = None
test_args.restoredir = None
test_args.public_id = None
test_args.gpg_keyring = None
test_args.gpg_homedir = None
test_args.gpg_binary = None

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_set_parameters__from_param(expanduser, Inventory, GPGOps):


    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['public_id'],
        saved_params['gpg_keyring'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)
    eq_(de.verbose, False)
    eq_(de.last_timestamp, saved_params['last_timestamp'])
    eq_(de.plaindir, saved_params['plaindir'])
    eq_(de.securedir, saved_params['securedir'])
    eq_(de.public_id, saved_params['public_id'])
    eq_(de.gpg_keyring, saved_params['gpg_keyring'])
    eq_(de.gpg_binary, saved_params['gpg_binary'])


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_set_parameters__from_args(expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    args = MagicMock()
    args.verbose = True
    args.plaindir = 'runtime_plaindir'
    args.securedir = 'runtime_securedir'
    args.restoredir = 'runtime_restoredir'
    args.public_id = 'runtime_public_id'
    args.gpg_keyring = 'runtime_gpg_keyring'
    args.gpg_homedir = 'runtime_gpg_homedir'
    args.gpg_binary = 'runtime_gpg_binary'

    expanduser.side_effect = [
        args.plaindir,
        args.securedir,
        args.restoredir,
        args.gpg_homedir,
        args.gpg_binary,
        args.plaindir,
        args.securedir,
        args.restoredir,
        args.gpg_homedir,
        args.gpg_binary
    ]

    de = DirEncryption(args)
    eq_(de.verbose, True)
    eq_(de.last_timestamp, saved_params['last_timestamp'])
    eq_(de.plaindir, args.plaindir)
    eq_(de.securedir, args.securedir)
    eq_(de.restoredir, args.restoredir)
    eq_(de.public_id, args.public_id)
    eq_(de.gpg_keyring, args.gpg_keyring)
    eq_(de.gpg_binary, args.gpg_binary)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_encrypt(expanduser, GPGOps):

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]
    inventory = MagicMock()

    de = DirEncryption(test_args)
    de.encrypt('plainfile', 'securefile', inventory)
    eq_(inventory.register.call_count, 1)
    de.gpg.encrypt.assert_called_once_with(
        os.path.join(saved_params['plaindir'], 'plainfile'),
        os.path.join(saved_params['securedir'], 'securefile')
    )


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.find_unencrypted_files')
@patch('direncrypt.direncryption.DirEncryption.encrypt')
def test_encrypt_all__no_files(encrypt, find, expanduser, Inventory, GPGOps):

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)
    de.encrypt_all()

    eq_(encrypt.call_count, 0)
    eq_(Inventory().__enter__().update_last_timestamp.call_count, 1)


@patch('direncrypt.direncryption.DirEncryption.encrypt_regular_files')
@patch('direncrypt.direncryption.DirEncryption.register_empty_dirs')
@patch('direncrypt.direncryption.DirEncryption.register_symlinks')
@patch('direncrypt.direncryption.DirEncryption.do_inv_maintenance')
def test_encrypt_all(maintenance, register_links, register_dirs, encrypt_files):

    de = DirEncryption(test_args)
    de.encrypt_all()

    eq_(maintenance.call_count, 1)
    eq_(register_links.call_count, 1)
    eq_(register_dirs.call_count, 1)
    eq_(encrypt_files.call_count, 1)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.find_unencrypted_files')
@patch('direncrypt.direncryption.DirEncryption.encrypt')
@patch('direncrypt.direncryption.FileOps.delete_file')
def test_encrypt_regular_files(delete_file, encrypt, find_ufiles, Inventory, GPGOps):

    find_ufiles.return_value = {
        'test_path_1': {'is_new': False},
        'test_path_2': {'is_new': False},
        'test_path_3': {'is_new': True}
    }

    de = DirEncryption(test_args)
    de.encrypt_regular_files(Inventory().__enter__().read_register("all"), Inventory().__enter__())

    eq_(encrypt.call_count, 3)
    eq_(delete_file.call_count, 2)
    eq_(find_ufiles.call_count, 1)
    eq_(encrypt.call_args_list[0][0][0], 'test_path_1')
    eq_(encrypt.call_args_list[1][0][0], 'test_path_2')
    eq_(encrypt.call_args_list[2][0][0], 'test_path_3')


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.register')
@patch('direncrypt.direncryption.DirEncryption.find_unregistered_empty_dirs')
def test_register_empty_dirs(find_udirs, register, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    find_udirs.return_value = {
        'test_dir_1': {'is_new': False},
        'test_dir_2': {'is_new': True}
    }

    de = DirEncryption(test_args)
    de.register_empty_dirs(Inventory().__enter__().read_register("dirs"), Inventory().__enter__())

    eq_(register.call_count, 2)
    eq_(find_udirs.call_count, 1)
    eq_(Inventory().__enter__().clean_record.call_count, 1)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.find_unregistered_links')
@patch('direncrypt.direncryption.DirEncryption.register')
def test_register_symlinks(register, find_ulinks, Inventory, GPGOps):

    find_ulinks.return_value = {
        'test_link_1': {'target': 'target_1', 'is_new': False},
        'test_link_2': {'target': 'target_2', 'is_new': True}
    }

    de = DirEncryption(test_args)
    de.register_symlinks(Inventory().__enter__().read_register("links"), Inventory().__enter__())

    eq_(register.call_count, 2)
    eq_(find_ulinks.call_count, 1)
    eq_(Inventory().__enter__().clean_record.call_count, 1)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.DirEncryption.clean')
def test_do_inv_maintenance(clean, Inventory, GPGOps):

    de = DirEncryption(test_args)
    de.do_inv_maintenance(Inventory().__enter__())

    eq_(clean.call_count, 1)
    eq_(Inventory().__enter__().update_last_timestamp.call_count, 1)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
def test_decrypt(expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    de = DirEncryption(test_args)
    de.decrypt('test_enc_file', 'test_restore_file', 'trustno1')

    de.gpg.decrypt.assert_called_once_with(
        os.path.join(saved_params['securedir'], 'test_enc_file'),
        os.path.join(saved_params['restoredir'], 'test_restore_file'),
        'trustno1'
    )


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.decrypt')
def test_decrypt_all__no_files(decrypt, expanduser,
                               Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    Inventory().__enter__().read_register.return_value = {}

    de = DirEncryption(test_args)
    de.decrypt_all('trustno1')

    eq_(de.decrypt.call_count, 0)


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.DirEncryption.decrypt')
@patch('direncrypt.direncryption.FileOps.create_symlink')
def test_decrypt_all(create_symlink, decrypt, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['public_id'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    Inventory().__enter__().read_register.return_value = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id'],
            'is_link': 0,
            'target': ''
        },
        'unenc_2': {
            'unencrypted_file': 'unenc_2',
            'encrypted_file': 'uuid-2',
            'public_id': 'some_other_id',
            'is_link': 0,
            'target': ''
        },
        'unenc_3': {
            'unencrypted_file': 'unenc_3',
            'encrypted_file': 'uuid-3',
            'public_id': saved_params['public_id'],
            'is_link': 0,
            'target': ''
        },
        'unenc_4': {
            'unencrypted_file': 'unenc_4',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 1,
            'target': 'target_4'
        },
        'unenc_5': {
            'unencrypted_file': 'unenc_5',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 1,
            'target': 'target_5'
        }

    }

    de = DirEncryption(test_args)
    de.decrypt_all('trustno1')

    eq_(de.decrypt.call_count, 2)
    eq_(create_symlink.call_count, 2)
    eq_(de.decrypt.call_args_list[0][0], ('uuid-1', 'unenc_1', 'trustno1'))
    eq_(de.decrypt.call_args_list[1][0], ('uuid-3', 'unenc_3', 'trustno1'))


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.walk')
def test_find_unencrypted_files__empty_dir(walk, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    register = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id'],
            'is_link': 0,
            'target': ''
        }
    }

    walk.return_value = []

    de = DirEncryption(test_args)
    files = de.find_unencrypted_files(register)

    eq_(files, {})


@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.walk')
@patch('direncrypt.direncryption.os.stat')
@patch('direncrypt.direncryption.os.path.islink')
def test_find_unencrypted_files(islink, stat, walk, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    register = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id'],
            'is_link': 0,
            'target': ''
        }
    }

    walk.return_value = [
        (saved_params['plaindir'], ['subdir_1'], ['unenc_1', 'unenc_2', 'unenc_3']),
        (os.path.join(saved_params['plaindir'], 'subdir_1'), [], ['unenc_4'])
    ]

    stat.return_value.st_mtime = 1234567895
    islink.return_value = True
    de = DirEncryption(test_args)
    files = de.find_unencrypted_files(register)
    eq_(len(files), 0)

    islink.reset_mock()
    islink.return_value = False
    files = de.find_unencrypted_files(register)
    eq_(len(files), 4)
    ok_('unenc_3' in files.keys())
    ok_(os.path.join('subdir_1', 'unenc_4') in files.keys())

    stat.reset_mock()
    stat.return_value.st_mtime = 1234567885
    files = de.find_unencrypted_files(register)
    eq_(len(files), 3)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.walk')
@patch('direncrypt.direncryption.os.stat')
@patch('direncrypt.direncryption.os.path.islink')
@patch('direncrypt.direncryption.os.readlink')
def test_find_unregistered_links(readlink, islink, stat, walk, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    register = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': '',
            'public_id': '',
            'is_link':1,
            'target': 'target_1'
        }
    }

    walk.return_value = [
        (saved_params['plaindir'], ['subdir_1'], ['unenc_1', 'unenc_2', 'unenc_3']),
        (os.path.join(saved_params['plaindir'], 'subdir_1'), [], ['unenc_4'])
    ]

    stat.return_value.st_mtime = 1234567895
    islink.return_value = True
    readlink.return_value = 'my_target'
    de = DirEncryption(test_args)
    links = de.find_unregistered_links(register)
    eq_(len(links), 6)
    ok_('unenc_3' in links.keys())
    ok_(os.path.join('subdir_1', 'unenc_4') in links.keys())

    stat.reset_mock()
    stat.return_value.st_mtime = 1234567885
    links = de.find_unregistered_links(register)
    eq_(len(links), 5)

    islink.reset_mock()
    islink.return_value = False
    links = de.find_unregistered_links(register)
    eq_(len(links), 0)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.walk')
@patch('direncrypt.direncryption.os.stat')
def test_find_unregistered_empty_dirs( stat, walk, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    register = {
        'subdir_1': {
            'unencrypted_file': 'subdir_1',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 0,
            'target': ''
        }
    }

    walk.return_value = [
        (saved_params['plaindir'], ['subdir_1'], ['unenc_1', 'unenc_2', 'unenc_3']),
        (os.path.join(saved_params['plaindir'], 'subdir_1'), [], [])
    ]

    stat.return_value.st_mtime = 1234567895
    de = DirEncryption(test_args)
    dirs = de.find_unregistered_empty_dirs(register)
    eq_(len(dirs), 1)
    ok_('subdir_1' in dirs.keys())

    stat.reset_mock()
    stat.return_value.st_mtime = 1234567885
    dirs = de.find_unregistered_empty_dirs(register)
    eq_(len(dirs), 0)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.path.isfile')
@patch('direncrypt.direncryption.os.listdir')
def test_clean_files(listdir, isfile, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    isfile.return_value = False
    inv = MagicMock()
    inv.read_register.return_value = {
        'unenc_1': {
            'unencrypted_file': 'unenc_1',
            'encrypted_file': 'uuid-1',
            'public_id': saved_params['public_id'],
            'is_link': 0,
            'target': ''
        },
        'unenc_2': {
            'unencrypted_file': 'unenc_2',
            'encrypted_file': 'uuid-2',
            'public_id': saved_params['public_id'],
            'is_link': 0,
            'target': ''
        }
    }
    de = DirEncryption(test_args)
    de.clean(inv)
    eq_(inv.clean_record.call_count, 6)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.path.islink')
@patch('direncrypt.direncryption.os.listdir')
def test_clean_links(listdir, islink, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    inv = MagicMock()
    inv.read_register.return_value = {
        'unenc_3': {
            'unencrypted_file': 'unenc_3',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 1,
            'target': 'link_3'
        },
        'unenc_4': {
            'unencrypted_file': 'unenc_4',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 1,
            'target': 'link_4'
        }
    }
    islink.return_value = False
    de = DirEncryption(test_args)
    de.clean(inv)
    eq_(inv.clean_record.call_count, 6)

@patch('direncrypt.direncryption.GPGOps')
@patch('direncrypt.direncryption.Inventory')
@patch('direncrypt.direncryption.os.path.expanduser')
@patch('direncrypt.direncryption.os.path.isdir')
@patch('direncrypt.direncryption.os.listdir')
def test_clean_dirs(listdir, isdir, expanduser, Inventory, GPGOps):

    Inventory().__enter__().read_parameters.return_value = saved_params

    expanduser.side_effect = [
        saved_params['plaindir'],
        saved_params['securedir'],
        saved_params['restoredir'],
        saved_params['gpg_homedir'],
        saved_params['gpg_binary']
    ]

    inv = MagicMock()
    inv.read_register.return_value = {
        'unenc_5': {
            'unencrypted_file': 'unenc_5',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 0,
            'target': ''
        },
        'unenc_6': {
            'unencrypted_file': 'unenc_6',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 0,
            'target': ''
        }
    }
    isdir.return_value = False
    de = DirEncryption(test_args)
    de.clean(inv)
    eq_(inv.clean_record.call_count, 6)

    inv.reset_mock()
    isdir.reset_mock()

    inv.read_register.return_value = {
        'unenc_7': {
            'unencrypted_file': 'unenc_7',
            'encrypted_file': '',
            'public_id': '',
            'is_link': 0,
            'target': ''
        }
    }
    isdir.return_value = True
    listdir.return_value = ['some_file']
    de.clean(inv)
    eq_(inv.clean_record.call_count, 3)
