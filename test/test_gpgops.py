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
from nose.tools import *
from mock import MagicMock, patch
from direncrypt.gpgops import GPGOps

@patch('direncrypt.gpgops.gnupg.GPG')
def test_encrypt(gpg):
    g = GPGOps(gpg_recipient='B183CAFE')

    fsrc = tempfile.NamedTemporaryFile()
    plainfile = fsrc.name
    encryptedfile = 'encryptedfile'
    g.encrypt(plainfile, encryptedfile)

    eq_(g.gpg.encrypt.call_count, 1)


@patch('direncrypt.gpgops.os')
@patch('direncrypt.gpgops.gnupg.GPG')
def test_decrypt(os, gpg):
    g = GPGOps(gpg_recipient='B183CAFE')

    fsrc = tempfile.NamedTemporaryFile()
    encryptedfile = fsrc.name
    plainfile = 'plainfile'
    phrase = 'trustno1'
    g.decrypt(encryptedfile, plainfile, phrase)

    eq_(g.gpg.decrypt.call_count, 1)
