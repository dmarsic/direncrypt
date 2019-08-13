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
import cmd
from direncrypt.inventory import Inventory

class CmdConfig(cmd.Cmd):
    """Command processor for configuration based on Cmd.

    This library can be used with the program using 'direncrypt'
    library, but is not needed by the library itself.
    """

    prompt = 'parameters> '

    def do_set_database(self, path):
        self.database = path

    def do_list(self, arg):
        """list

        Prints all stored settings."""
        print('%-15s %s' % ('PARAMETER', 'VALUE'))
        print('-' * 40)
        with Inventory(self.database) as i:
            params = i.read_parameters(params_only=True)
            for key, value in i.read_parameters(params_only=True).items():
                print('%-15s %s' % (key, value))
        print()

    def do_plaindir(self, directory):
        """plaindir [directory]

        Store directory location for unencrypted files.
        Ex: /home/myself/DropboxLocal"""
        self.update('plaindir', directory)

    def do_securedir(self, directory):
        """securedir [directory]

        Store directory location for encrypted files.
        Ex: /home/myself/Dropbox/Encrypted"""
        self.update('securedir', directory)

    def do_public_id(self, id):
        """public_id [gpg_public_id]

        Store GPG public ID used for file encryption.
        Ex: C0FF3E33"""
        self.update('public_id', id)

    def do_gpg_keyring(self, filename):
        """gpg_keyring [filename]

        Store GPG keyring filename.
        Ex: pubring.kbx"""
        self.update('gpg_keyring', filename)

    def do_gpg_homedir(self, directory):
        """gpg_homedir [directory]

        Store GPG home directory.
        Ex: /home/myself/.gnupg"""
        self.update('gpg_homedir', directory)

    def do_gpg_binary(self, filename):
        """gpg_binary [filename]

        Store GPG binary filename.
        Ex: /usr/bin/gpg2"""
        self.update('gpg_binary', filename)

    def update(self, key, value):
        """Generic function to update a single parameter."""
        print('Setting %s to: %s' % (key, value))
        with Inventory(self.database) as i:
            i.update_parameters(key, value)

    def do_done(self, line):
        """Finish setting up configuration."""
        return True

    def do_exit(self, line):
        """Finish setting up configuration, alternative function."""
        return True


class RunConfig(object):
    """Run command processor.

    This enables users to interactively set parameters used by direncrypt.
    The parameters are saved into the database and are used as default if
    they are not specified on each run as command-line arguments.
    """

    def __init__(self, database=None):
        """Describe usage and process set parameters."""
        print('Use "<parameter_name> <value>" to set parameter value.')
        print('Use "list" to print current values, or "done" to exit.')
        print('Enter "help [<parameter>]" for additional help.')
        print()

        if database is None:
            database = 'inventory.sqlite'

        cc = CmdConfig()
        cc.do_set_database(database)
        cc.do_list(None)
        cc.cmdloop()
