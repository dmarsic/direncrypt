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
from inventory import Inventory
from direncryption import DirEncryption

class ConsistencyCheck:
    """Consistency checks between unencrypted and encrypted directories.

    Checks are performed based on the file register, which is kept in
    inventory.sqlite database.
    """

    def __init__(self, database):
        """Load registered file list and program parameters.

        Program parameters are needed for file locations.
        """
        self.database = database
        with Inventory(self.database) as inventory:
            self.parameters = inventory.read_parameters()
            self.fileset = inventory.read_register()

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
        for filename in self.fileset:

            unenc_full_path = os.path.expanduser(os.path.join(
                    self.parameters['plaindir'],
                    self.fileset[filename]['unencrypted_file']))
            self.fileset[filename]['unencrypted_file_check'] = \
                    os.path.exists(unenc_full_path)

            enc_full_path = os.path.expanduser(os.path.join(
                    self.parameters['securedir'],
                    self.fileset[filename]['encrypted_file']))
            self.fileset[filename]['encrypted_file_check'] = \
                    os.path.exists(enc_full_path)

    def delete_file(self, directory, filename):
        """Try to delete file from filesystem."""
        print "Deleting file on filesystem: {}".format(filename)
        try:
            os.unlink(os.path.expanduser(os.path.join(directory, filename)))
        except OSError as e:
            print "Failed to delete {}: {}".format(filename, str(e))
            return False

        return True

    def clean_registry(self, filename):
        """Clean entry from registry."""
        print "Cleaning from registry: {}".format(filename)
        with Inventory(self.database) as inventory:
            inventory.clean_record(filename)

        return True

    def loop_through(self, clean=False, resync=False):
        """Go through all entries and take action based on user input.

        This method can be called after check() has been executed,
        otherwise it cannot properly report on the existence of
        files.
        """
        count_nok = 0
        total_files = len(self.fileset)

        print 'Plaindir:', self.parameters['plaindir']
        print 'Securedir:', self.parameters['securedir']
        print '\nSTATUS PLAINFILE' + ' ' * 26 + ' ENCFILE'

        for filename, entry in self.fileset.iteritems():

            unenc_exists = 'u'
            enc_exists = 'e'
            status = 'ok'

            if not entry['unencrypted_file_check']:
                unenc_exists = ''
            if not entry['encrypted_file_check']:
                enc_exists = ''

            if clean and (not unenc_exists or not enc_exists):
                if unenc_exists:
                    print "delete unenc"
                    self.delete_file(self.parameters['plaindir'],
                                     entry['unencrypted_file'])

                if enc_exists:
                    print "delete enc"
                    self.delete_file(self.parameters['securedir'],
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


            print '%-3s %1s%1s %-35s %-30s' % (status, unenc_exists, enc_exists,
                    self.fileset[filename]['unencrypted_file'],
                    self.fileset[filename]['encrypted_file'])

        print '\nTotal files in the register:', total_files
        print 'Check: %d ok, %d not ok' % (total_files - count_nok, count_nok)
