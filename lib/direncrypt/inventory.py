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

    def read_all_register(self):
        """Get information on all registered regular files and symlinks.

        Returns a dict with unencrypted filename for keys, having
        a dict of unencrypted file, encrypted file, public id,
        is_link and target as value.
        """
        rows = {}
        request = """SELECT unencrypted_file, encrypted_file, public_id,
                     is_link, target FROM register"""
        for row in self.cursor.execute(request):
            rows[row[0]] = {
                'unencrypted_file': row[0],
                'encrypted_file':   row[1],
                'public_id':        row[2],
                'is_link':          row[3],
                'target':           row[4]
            }
        return rows
    
    def read_registered_files(self):
        """Get information on all registered regular files.

        Returns a dict with unencrypted filename for keys, having
        a dict of unencrypted file, encrypted file, public id,
        is_link and target as value.
        """
        rows = {}
        request = """SELECT unencrypted_file, encrypted_file, public_id,
                     is_link, target FROM register WHERE is_link=0 and
                     encrypted_file IS NOT NULL"""
        for row in self.cursor.execute(request):
            rows[row[0]] = {
                'unencrypted_file': row[0],
                'encrypted_file':   row[1],
                'public_id':        row[2],
                'is_link':          row[3],
                'target':           row[4]
            }
        return rows
    
    def read_registered_links(self):
        """Get information on all registered links.
        
        Returns a dict with unencrypted filename for keys, having
        a dict of unencrypted file, encrypted file, public id,
        is_link and target as value.
        """
        rows = {}
        request = """SELECT unencrypted_file, encrypted_file, public_id, 
                     is_link, target FROM register WHERE is_link=1"""
        for row in self.cursor.execute(request):
            rows[row[0]] = {
                'unencrypted_file': row[0],
                'encrypted_file':   row[1],
                'public_id':        row[2],
                'is_link':          row[3],
                'target':           row[4]
            }
        return rows
    
    def read_registered_dirs(self):
        """Get information on all registered empty directories.
        
        Returns a dict with unencrypted filename for keys, having
        a dict of unencrypted file, encrypted file, public id,
        is_link and target as value.
        """
        rows = {}
        request = """SELECT unencrypted_file, encrypted_file, public_id,
                     is_link, target FROM register WHERE is_link=0 and
                     encrypted_file IS NULL"""
        for row in self.cursor.execute(request):
            rows[row[0]] = {
                'unencrypted_file': row[0],
                'encrypted_file':   row[1],
                'public_id':        row[2],
                'is_link':          row[3],
                'target':           row[4]
            }
        return rows
    
    def read_line_from_register(self, plainfile):
        """Get encrypted filename from unencrypted filename in register"""
        result = {}
        request = "SELECT encrypted_file FROM register WHERE unencrypted_file = ?"
        for row in self.cursor.execute(request, (plainfile,)):
            result[plainfile] = {'encrypted_file':   row[0]}
        return result[plainfile]['encrypted_file']

    def register(self, plain_path, enc_path, public_id, is_link, target):
        """Register input and output filenames into a database."""
        is_link_int = 0 if is_link==False else 1
        self.cursor.execute('''INSERT OR REPLACE INTO register
            (unencrypted_file, encrypted_file, public_id, is_link, target)
            VALUES (?,?,?,?,?)''',
            (plain_path, enc_path, public_id, is_link_int, target))

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
        request = "DELETE FROM register WHERE unencrypted_file = ?"
        self.cursor.execute(request, (filename,))
        
    def exists_encrypted_file(self, filename):
        """tests if an encoded filename exists in register.
        
        Returns True if 'filename' is found, False otherwise.
        """
        request = "SELECT encrypted_file FROM register WHERE encrypted_file = ?"
        self.cursor.execute(request, (filename,))
        enc_filenames = self.cursor.fetchall()
        nb = len(enc_filenames)
        result = True if nb==1 else False
        return result
