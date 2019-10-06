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
import glob
import sqlite3
from typing import List
from direncrypt import ROOTDIR


class DatabaseBuilder(object):
    """Builds/rebuilds inventory database.

    Inventory database needs to exist before the first execution
    of direncrypt. This class removes the need for building it
    manually.

    Once built, there is generally no reason to rebuild it.
    REBUILDING WILL DELETE THE PREVIOUS DATABASE, WHICH MAY CAUSE YOU
    GREAT PAIN ON DECRYPTING. Keep your backup safe.
    """

    SQL_FILES_PATH = os.path.join(ROOTDIR, 'sql', '*')

    def __init__(self, path: str) -> None:
        """Constructor.

        :param path: Path to the inventory database.
        """
        self.database_path = path

    def exists(self) -> bool:
        """Checks if inventory database file exists."""
        return os.path.exists(self.database_path)

    def build(self, force: bool = False) -> None:
        """Creates inventory database.

        If it exists, it won't recreate it, unless `force` is set.
        SETTING `force` WILL DELETE YOUR EXISTING DATABASE.

        :param force: Set if the database should be recreated. It deletes
                      the previos database if it exists.
        """
        print(f'Inventory database file: {self.database_path}')
        if self.exists() and not force:
            return
        if self.exists() and force:
            os.unlink(self.database_path)
            print('Removed previous database.')
        conn = sqlite3.connect(self.database_path)
        for sql_file in sorted(glob.glob(self.SQL_FILES_PATH)):
            with open(sql_file, 'r') as f:
                conn.executescript(f.read())
        conn.commit()
        conn.close()
        print('Database created.')
