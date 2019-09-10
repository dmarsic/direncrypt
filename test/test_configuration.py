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

import nose
from nose.tools import *
from mock import MagicMock, patch
from direncrypt.configuration import CmdConfig, RunConfig

@patch('direncrypt.configuration.Inventory')
def test_update(Inventory):
    cmdconfig = CmdConfig()
    cmdconfig.do_set_database('test_database')
    cmdconfig.update('key_1', 'value_1')

    eq_(Inventory().__enter__().update_parameters.call_count, 1)

    args = Inventory().__enter__().update_parameters.call_args
    parameters = args[0]
    eq_(parameters[0], 'key_1')
    eq_(parameters[1], 'value_1')

@patch('direncrypt.configuration.CmdConfig')
def test_RunConfig(CmdConfig):
    runconfig = RunConfig()
    eq_(CmdConfig().cmdloop.call_count, 1)
