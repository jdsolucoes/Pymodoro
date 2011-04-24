#!/usr/bin/env python2.6
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

import sqlite3 as _s
from sql import AbstractSQL
import os

class db(AbstractSQL):
    
    def connect(self):
        dir = os.path.expanduser('~/.pymodoro')
        try:        
            if os.path.isdir(dir):    
                self.conn = _s.connect("%s/pymodoro.db" % dir,detect_types = _s.PARSE_DECLTYPES)
            else:
                try:
                    os.mkdir(dir)
                    self.conn = _s.connect("%s/pymodoro.db" % dir,detect_types = _s.PARSE_DECLTYPES)
                except:
                    exit('Erro ao criar diretorio')
            self.cursor = self.conn.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS tarefas(id INTEGER PRIMARY KEY, concluido int, tarefa text, pomodoros int, data timestamp )")
            
            return True
        except:
            return None
        
    
    def getByDate(self,day=None,month=None,year=None):
        
        """Recives an day, month and year and returns everything that founds"""
        
        t = []
        c = []
        if day:
            
            t.append(u'%d')
            c.append(str(day))
        if month:
            if month < 10:
                c.append("0"+str(month))
            else:
                c.append(str(month))
            t.append(u'%m')
            
        if year:
            t.append(u'%Y')
            c.append(str(year))
            
        
  
        z = "-".join(t)
        v = "-".join(c)
        
        sql = "SELECT * FROM `tarefas` WHERE strftime('%s',data) = '%s' " %(z,v)

        self.cursor.execute(sql)
        return self.cursor.fetchall()
           
    
    def disconnect(self):
        self.conn.commit()
        self.conn.close()
        
        
        



