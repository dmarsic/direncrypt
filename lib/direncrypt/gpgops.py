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

import gnupg
import os

class GPGOps:
    """A simple wrapper for GPG encryption/decryption.

    The class provides functions for encrypting and decrypting a single
    file. GPG parameters needed to execute encryption functions are set
    during the instantiation of the class.
    """

    def __init__(self,
                 gpg_binary='gpg2',
                 gpg_recipient=None,
                 gpg_homedir=os.path.expanduser('~/.gnupg'),
                 gpg_keyring='pubring.kbx',
                 verbose=False):
        """Set GPG parameters for encrypt/decrypt operations."""
        self.recipient = gpg_recipient
        self.gpg = gnupg.GPG(gpgbinary=gpg_binary,
                             gnupghome=gpg_homedir,
                             keyring=gpg_keyring,
                             verbose=verbose)

    def encrypt(self, plainfile, encfile):
        """Encrypt content from plainfile into encfile."""
        with open(plainfile, mode = 'rb') as f:
            self.gpg.encrypt(f.read(),
                             self.recipient,
                             armor=False,
                             output=encfile)

    def decrypt(self, encfile, plainfile, phrase):
        """Decrypt content from encfile into plainfile."""
        plaindir = os.path.dirname(plainfile)
        if not os.path.exists(plaindir):
            os.makedirs(plaindir)

        with open(encfile, mode='rb') as f:
            self.gpg.decrypt(f.read(),
                             passphrase=phrase,
                             output=plainfile)
