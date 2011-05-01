#!/usr/bin/env python
#-*- coding: utf-8 -*-
#   This file is part of Pymodoro.

#   Pymodoro is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.

#   Pymodoro is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Pymodoro.  If not, see <http://www.gnu.org/licenses/>.


import MySQLdb
from sql import AbstractSQL

class db(AbstractSQL):
    
    def connect(self):
        #try to connect to the database, here, mysql.
        try:
            self.db = MySQLdb.connect(
                self.db_config['host'],
                self.db_config['user'],
                self.db_config['password'],
                self.db_config['db_name']
                )
            self.cursor = self.db.cursor()
            return True
        except:
            return False
   