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


import tempfile
import nose
from nose.tools import ok_, eq_
from mock import MagicMock, patch
from direncrypt.gpgops import GPGOps

@patch('direncrypt.gpgops.gnupg.GPG')
@patch('builtins.open')
def test_encrypt_ok(open, GPG):
    """Successful encryption sets 'ok' attribute to True."""
    crypt_result = MagicMock()
    crypt_result.ok = True
    GPG.encrypt.return_value = crypt_result

    g = GPGOps(gpg_recipient='B183CAFE')
    result = g.encrypt('plainfile', 'encryptedfile')

    ok_(result.ok)


@patch('direncrypt.gpgops.gnupg.GPG')
@patch('builtins.open')
def test_encrypt_fail(open, GPG):
    """Unsuccessful encryption sets 'ok' attribute to False."""
    crypt_result = MagicMock()
    crypt_result.ok = False
    GPG.encrypt.return_value = crypt_result

    g = GPGOps(gpg_recipient='B183CAFE')
    result = g.encrypt('plainfile', 'encryptedfile')

    not ok_(result.ok)


@patch('direncrypt.gpgops.gnupg.GPG')
@patch('builtins.open')
@patch('direncrypt.gpgops.os')
def test_decrypt_ok(os, open, GPG):
    """Successful decryption sets 'ok' attribute to True."""
    crypt_result = MagicMock()
    crypt_result.ok = True
    GPG.encrypt.return_value = crypt_result

    g = GPGOps(gpg_recipient='B183CAFE')
    result = g.decrypt('encryptedfile', 'plainfile', 'phrase')

    ok_(result.ok)


@patch('direncrypt.gpgops.gnupg.GPG')
@patch('builtins.open')
@patch('direncrypt.gpgops.os')
def test_decrypt_ok(os, open, GPG):
    """Successful decryption sets 'ok' attribute to False."""
    crypt_result = MagicMock()
    crypt_result.ok = False
    GPG.encrypt.return_value = crypt_result

    g = GPGOps(gpg_recipient='B183CAFE')
    result = g.decrypt('encryptedfile', 'plainfile', 'phrase')

    not ok_(result.ok)
