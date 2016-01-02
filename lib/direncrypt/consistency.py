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

        with Inventory(database) as inventory:
            self.parameters = inventory.read_parameters()
            self.fileset = inventory.read_register()

    def check(self):

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

    def print_formatted(self):

        count_nok = 0
        total_files = len(self.fileset)

        print 'Plaindir:', self.parameters['plaindir']
        print 'Securedir:', self.parameters['securedir']
        print '\nSTATUS PLAINFILE' + ' ' * 26 + ' ENCFILE'

        for filename in self.fileset:

            unenc_exists = 'u'
            enc_exists = 'e'
            status = 'ok'

            if not self.fileset[filename]['unencrypted_file_check']:
                unenc_exists = ''
            if not self.fileset[filename]['encrypted_file_check']:
                enc_exists = ''
            if not unenc_exists or not enc_exists:
                status = 'NOK'
                count_nok += 1

            print '%-3s %1s%1s %-35s %-30s' % (status, unenc_exists, enc_exists,
                    self.fileset[filename]['unencrypted_file'],
                    self.fileset[filename]['encrypted_file'])

        print '\nTotal files in the register:', total_files
        print 'Check: %d ok, %d not ok' % (total_files - count_nok, count_nok)
