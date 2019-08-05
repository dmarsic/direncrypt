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

import sqlite3

class Inventory:
    """Inventory is a file/location register for encrypted files.

    This class, used with 'with' statement, defines the connection.
    Provided methods use cursor to execute queries against the
    database. Calling functions and classes should not directly use
    cursor to execute arbitrary queries.
    """

    def __init__(self, filename):
        """Set database name."""
        self.database = filename

    def __enter__(self):
        self.conn = sqlite3.connect(self.database)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def read_parameters(self, params_only=False):
        """Fetch program parameters and state from the database."""
        params = {}
        for row in self.cursor.execute('SELECT key, value FROM parameters'):
            params[row[0]] = row[1]
        if not params_only:
            for row in self.cursor.execute('SELECT key, value FROM state'):
                params[row[0]] = row[1]
        return params

    def read_register(self):
        """Get information on all registered encrypted files.

        Returns a dict with unencrypted filename for keys, having
        a dict of unencrypted file, encrypted file and public id
        as value.
        """
        rows = {}
        for row in self.cursor.execute('''
                SELECT unencrypted_file, encrypted_file, public_id
                FROM register'''):
            rows[row[0]] = {
                'unencrypted_file': row[0],
                'encrypted_file':   row[1],
                'public_id':        row[2]
            }
        return rows
    
    def read_line_from_register(self, plainfile):
        """Get encrypted filename from unencrypted filename in register"""
        result = {}
        for row in self.cursor.execute('''
                SELECT encrypted_file FROM register WHERE unencrypted_file = ? ''',(plainfile,)):
            result[plainfile] = {'encrypted_file':   row[0]}
        return result[plainfile]['encrypted_file']

    def register(self, plain_path, enc_path, public_id):
        """Register input and output filenames into a database."""
        self.cursor.execute('''INSERT OR REPLACE INTO register
            (unencrypted_file, encrypted_file, public_id)
            VALUES (?,?,?)''',
            (plain_path, enc_path, public_id))

    def update_last_timestamp(self):
        """Update last timestamp in the database."""
        self.cursor.execute('''UPDATE state SET value = strftime('%s', 'now')
            WHERE key = 'last_timestamp' ''')

    def update_parameters(self, key, value):
        """Update program parameters."""
        self.cursor.execute('''UPDATE parameters
            SET value = ? WHERE key = ? ''', (value, key))

    def clean_record(self, filename):
        """Delete record based on the unencrypted filename."""
        self.cursor.execute(
                '''DELETE FROM register WHERE unencrypted_file = ?''',
                (filename,))
