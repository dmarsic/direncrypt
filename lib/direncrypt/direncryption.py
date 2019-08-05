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

import os
import uuid
import logging
from gpgops import GPGOps
from inventory import Inventory
from fileops import FileOps

class DirEncryption:
    """DirEncryption encrypts and decrypts files between two directories.

    One directory serves as a repository of unencrypted files, and the
    other contains encrypted version of the same files.

    DirEncryption uses a SQLite database as a register of known files.
    Files from the source (unencrypted) directory will be encrypted
    into the destination directory if the modified time of a file
    is newer than the time of the last run.
    """

    def __init__(self, args, database=None):
        """Set program parameters and initialize GPG operations object."""
        if database is None:
            self.database = 'inventory.sqlite'
        else:
            self.database = database

        self.set_parameters(args)
        self.gpg = GPGOps(gpg_binary=self.gpg_binary,
                          gpg_recipient=self.public_id,
                          gpg_keyring=self.gpg_keyring)

    def set_parameters(self, args):
        """Set parameters based on database config and passed args."""
        self.verbose = False
        if args and args.verbose:
            self.verbose = True

        with Inventory(self.database) as i:
            parameters = i.read_parameters()
        for parameter, value in parameters.iteritems():
            self._print('Parameters: {:<15} : {}', parameter, value)


        self.last_timestamp = parameters['last_timestamp']

        self.plaindir    = os.path.expanduser(parameters['plaindir'])
        self.securedir   = os.path.expanduser(parameters['securedir'])
        self.public_id   = parameters['public_id']
        self.gpg_keyring = parameters['gpg_keyring']
        self.gpg_homedir = os.path.expanduser(parameters['gpg_homedir'])
        self.gpg_binary  = os.path.expanduser(parameters['gpg_binary'])

        if args is None:
            return

        if args.plaindir:
            self.plaindir    = os.path.expanduser(args.plaindir)
        if args.securedir:
            self.securedir   = os.path.expanduser(args.securedir)
        if args.public_id:
            self.public_id   = args.public_id
        if args.gpg_keyring:
            self.gpg_keyring = args.gpg_keyring
        if args.gpg_homedir:
            self.gpg_homedir = os.path.expanduser(args.gpg_homedir)
        if args.gpg_binary:
            self.gpg_binary  = os.path.expanduser(args.gpg_binary)

    
    
    def encrypt_all(self):
        """Encrypt all new files from unencrypted directory.

        New files are those that have modified timestamp newer than
        the timestamp of the last run. At the end of run, the timestamp
        is updated.

        The files are recursively searched for in the source directory.
        """
        register = {}
        with Inventory(self.database) as i:
            register = i.read_register()
            files = self.find_unencrypted_files(register) 
            for plainfile, val in files.items():
                if not val['is_new']:
                    # remove old file in secure directory
                    encfile = i.read_line_from_register(plainfile)
                    FileOps.delete_file(self.securedir, encfile)
                encryptedfile = self.generate_name()
                self.encrypt(plainfile, encryptedfile)
                self._print('Encrypted: {} ---> {}', plainfile, encryptedfile)
            i.update_last_timestamp()

    def encrypt(self, plainfile, encfile):
        """Encrypt the file and register input and output filenames."""
        plain_path = os.path.join(self.plaindir, plainfile)
        encrypted_path = os.path.join(self.securedir, encfile)

        with Inventory(self.database) as i:
            i.register(plainfile, encfile, self.public_id)
        self.gpg.encrypt(plain_path, encrypted_path)

    def decrypt_all(self, passphrase):
        """Decrypt all files from encrypted source.

        Files that are being decrypted must be registered under the same
        public id in the database, so the passed passphrase would work
        for dectyption process.
        """
        register = {}
        with Inventory(self.database) as i:
            register = i.read_register()
            for filename, record in register.iteritems():
                if record['public_id'] != self.public_id:
                    continue
                try:
                    self.decrypt(record['encrypted_file'],
                             record['unencrypted_file'],
                             passphrase)
                except IOError as e:
                    logging.warning('decrypt_all: {}'.format(e))

    def decrypt(self, encfile, plainfile, phrase):
        """Decrypt the file using a supplied passphrase."""
        encrypted_path = os.path.join(self.securedir, encfile)
        plain_path = os.path.join(self.plaindir, plainfile)
        self.gpg.decrypt(encrypted_path, plain_path, phrase)
        self._print('Decrypt: {} ---> {}',
                encrypted_path, plain_path)

    def find_unencrypted_files(self, register):
        """List all files that need to be encrypted.

        os.walk does not expand tilde in paths, so the walk directory
        is explicitly expanded.

        register is the currently known list of encrypted files.

        Returns a dict, with relative path of the unencrypted files
        for keys, and a dict with modified time key-value pair and
        is_new boolean flag for values.
        """
        files = {}
        self._print('Walking: {}', self.plaindir)

        for (dirpath, dirnames, filenames) in os.walk(self.plaindir):
            for name in filenames:
                filepath = os.path.join(dirpath, name)
                statinfo = os.stat(filepath)
                mtime = statinfo.st_mtime
                relative_path = filepath[(len(self.plaindir) + 1):]
                if relative_path not in register:
                    # new file
                    enc_flag = '*'
                    files[relative_path] = {'modified_time': mtime, 'is_new':True}
                elif relative_path in register and mtime > int(self.last_timestamp):
                    # file exists and has changed since last run
                    enc_flag = '*'
                    files[relative_path] = {'modified_time': mtime, 'is_new':False}
                else:
                    # file is not changed since last run
                    enc_flag = ' '
                self._print('List files: {} {} ({}): {}',
                        enc_flag, int(mtime), self.last_timestamp,
                        relative_path)
        return files

    def generate_name(self):
        """Return a unique file name for encrypted file."""
        return str(uuid.uuid4())

    def _print(self, message, *args):
        """Internal method to print messages to STDOUT."""
        uargs = []
        for a in args:
            if isinstance(a, basestring):
                a = a.encode('utf-8', errors='replace')
            uargs.append(a)
        if self.verbose:
            print message.format(*uargs)
