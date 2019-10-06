#!/usr/bin/env python

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

"""This program encrypts files from the source directory to the
destination directory, or decrypts files from the destination
directory to the source directory, using GPG.

GPG configuration should already be set up on the executing host.

The program uses a register in the form of SQLite database to know
which files have already been processed and with which public ID.

See README.md for the full description.

Sample usage:
(1) Program is already configured, encrypt all files that have not
    been encrypted since the last run:

      encrypt.py -e

(2) Program is already configured, decrypt all files found in
    register from encrypted (destination) to source directory:

      encrypt.py -d

(3) Program is not yet configured, or we want to override some
    parameters, and encrypt unencrypted files:

      encrypt.py --encrypt \
                 --plaindir ~/DropboxLocal \
                 --securedir ~/Dropbox/Enc \
                 --restoredir ~/DropboxRestore \
                 --public-id BADCOFFE \
                 --gpg-homedir ~/.gnupg \
                 --gpg-keyring pubring.kbx \
                 --gpg-binary gpg2
"""

import argparse
import getpass
from direncrypt import DATABASE
from direncrypt.configuration import RunConfig
from direncrypt.direncryption import DirEncryption


def header():
    print("""direncrypt  Copyright (C) 2015  Domagoj Marsic
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; see 'LICENSE' file for details.
""")


if __name__ == '__main__':
    database = DATABASE

    parser = argparse.ArgumentParser(
            description='Encrypt and transfer files between two directories.')
    parser.add_argument('-e', '--encrypt',
            action='store_true',
            help='Encrypt and transfer files from unencrypted source')
    parser.add_argument('-d', '--decrypt',
            action='store_true',
            help='Decrypt and transfer files from encrypted source')
    parser.add_argument('--configure',
            action='store_true',
            help='Configure parameters interactively')
    parser.add_argument('-v', '--verbose',
            action='store_true',
            help='Print verbose messages during execution')

    parser.add_argument('-p', '--plaindir',    help='Unencrypted directory')
    parser.add_argument('-s', '--securedir',   help='Encrypted directory')
    parser.add_argument('-r', '--restoredir',  help='Restore directory')
    parser.add_argument('-i', '--public-id',   help='GPG public id')
    parser.add_argument('-P', '--passphrase',
            help='Passphrase to decrypt files.')
    parser.add_argument('-H', '--gpg-homedir', help='GPG home directory')
    parser.add_argument('-k', '--gpg-keyring', help='GPG keyring file')
    parser.add_argument('-b', '--gpg-binary',  help='GPG binary file')

    args = parser.parse_args()

    if args.configure:
        header()
        c = RunConfig(database=database)
    elif args.encrypt:
        e = DirEncryption(args, database=database)
        e.encrypt_all()
    elif args.decrypt:
        if args.passphrase:
            passphrase = args.passphrase
        else:
            passphrase = getpass.getpass('Passphrase: ')
        e = DirEncryption(args, database=database)
        e.decrypt_all(passphrase)
    else:
        header()
        print('Please specify encrypt (-e) or decrypt (-d) operation,')
        print('or --configure to set up configuration.')
