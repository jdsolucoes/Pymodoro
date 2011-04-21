#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

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
   