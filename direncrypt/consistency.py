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

import os
from direncrypt.inventory import Inventory
from direncrypt.direncryption import DirEncryption
from direncrypt.fileops import FileOps


class ConsistencyCheck(object):
    """Consistency checks between unencrypted and encrypted directories.

    Checks are performed based on the file register, which is kept in
    inventory.sqlite database.
    """

    def __init__(self, database):
        """Load program parameters.

        Program parameters are needed for file locations.
        """
        self.database = database
        with Inventory(self.database) as inventory:
            self.parameters = inventory.read_parameters()

    def set_passphrase(self, passphrase):
        """Set passphrase to be used for decrypting."""
        self.passphrase = passphrase

    def check(self):
        """Check file existence based on the register file set.

        Both unencrypted and encrypted files are checked in their
        respective plain and encrypted directories. A flag is set
        based on the check and fileset dict is updated.

        This method does not report or do anything else, so another
        method may be required to show the result of the check.
        """
        # Load registered file list.
        with Inventory(self.database) as inventory:
            self.registered_files = inventory.read_register("files")

        for filename in self.registered_files:

            unenc_full_path = os.path.expanduser(os.path.join(
                    self.parameters['plaindir'],
                    self.registered_files[filename]['unencrypted_file']))
            self.registered_files[filename]['unencrypted_file_check'] = \
                    os.path.exists(unenc_full_path)

            enc_full_path = os.path.expanduser(os.path.join(
                    self.parameters['securedir'],
                    self.registered_files[filename]['encrypted_file']))
            self.registered_files[filename]['encrypted_file_check'] = \
                    os.path.exists(enc_full_path)

    def clean_registry(self, filename):
        """Clean entry from registry."""
        print("Cleaning from registry: {}".format(filename))
        with Inventory(self.database) as inventory:
            inventory.clean_record(filename)

    def loop_through(self, clean=False, resync=False):
        """Go through all entries and take action based on user input.

        This method can be called after check() has been executed,
        otherwise it cannot properly report on the existence of
        files.
        """
        count_nok = 0
        total_files = len(self.registered_files)

        print('Plaindir: {}'.format(self.parameters['plaindir']))
        print('Securedir: {}'.format(self.parameters['securedir']))
        print('\nSTATUS PLAINFILE{}ENCFILE'.format(' '*27))

        for filename, entry in self.registered_files.items():

            unenc_exists = 'u'
            enc_exists = 'e'
            status = 'ok'

            if not entry['unencrypted_file_check']:
                unenc_exists = ''
            if not entry['encrypted_file_check']:
                enc_exists = ''

            if clean and (not unenc_exists or not enc_exists):
                if unenc_exists:
                    print("delete unenc")
                    FileOps.delete_file(self.parameters['plaindir'],
                                     entry['unencrypted_file'])

                if enc_exists:
                    print("delete enc")
                    FileOps.delete_file(self.parameters['securedir'],
                                     entry['encrypted_file'])

                self.clean_registry(entry['unencrypted_file'])
                total_files -= 1
            elif not unenc_exists and resync:
                de = DirEncryption(None, self.database)
                de.decrypt(entry['encrypted_file'],
                           entry['unencrypted_file'],
                           self.passphrase)
                unenc_exists = 'u'
            elif not unenc_exists or not enc_exists:
                status = 'NOK'
                count_nok += 1


            print('%-3s %1s%1s %-35s %-30s' % (status, unenc_exists, enc_exists,
                    self.registered_files[filename]['unencrypted_file'],
                    self.registered_files[filename]['encrypted_file']))

        print('\nTotal files in the register: {}'.format(total_files))
        print('Check: {} ok, {} not ok'.format(total_files - count_nok, count_nok))

    def delete_orphans_encrypted_files(self):
        """Delete orphans encoded files (which are not in register).

        Normally this should not happen, but it can happen anyway
        after a crash during encryption or by modifying register
        manually.
        """
        with Inventory(self.database) as inv:
            enc_files = list()
            for (dirpath, dirnames, filenames) in os.walk(self.parameters['securedir']):
                for name in filenames:
                    enc_files.append(name)
            for enc_file in enc_files:
                if not inv.exists_encrypted_file(enc_file):
                    FileOps.delete_file(self.parameters['securedir'], enc_file)

    def list_records(self):
        "Display number of records."

        with Inventory(self.database) as inv:
            total_records = len(inv.read_register("all"))
            reg_files = len(inv.read_register("files"))
            reg_links = len(inv.read_register("links"))
            reg_dirs = len(inv.read_register("dirs"))

            print("- Registered regular files :     {}".format(reg_files))
            print("- Registered symlinks :          {}".format(reg_links))
            print("- Registered empty directories : {}".format(reg_dirs))
            print()
            print("Total number of records :        {}".format(total_records))
