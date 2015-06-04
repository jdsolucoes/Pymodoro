#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

# The Sql generator, stand on your motherfucker feet.


class AbstractSQL(object):

    def getAll(self, table=None, **kwarg):
        """GOGOHORSE"""

        if table:
            key = kwarg.keys()[0]
            valor = kwarg[key]
            sql = "SELECT * FROM `%s` WHERE %s = '%s'" % (table, key, valor)
            self.cursor.execute(sql)
            return self.cursor.fetchall()

    def getByID(self, id=None):
        """Get all from tarefas where ID = ID"""
        if id:
            self.cursor.execute(
                "SELECT * FROM `tarefas` WHERE id = '%s' " % id)
            return self.cursor.fetchone()

    def getByDate(self, day=None, month=None, year=None):
        """Recives an day, month and year and returns everything that founds"""
        sql = "SELECT * FROM `tarefas` WHERE "
        termo = []
        if day:
            termo.append("DAY(data) = '%s'" % day)
        if year:
            termo.append("YEAR(data) = '%s'" % year)
        if month:
            termo.append("MONTH(data) = '%s'" % month)
        query = " AND ".join(termo)
        sql += query
        sql += " ORDER BY id ASC"

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update(self, table=None, id=None, **kwargs):
        """Receives a table name, the ID and the data to change"""
        arg = {}
        arg.update(kwargs)

        for key, value in arg.items():
            arg[key] = (str(value), repr(value))[type(value) == str]
        a = 'SET %s' % ', '.join(
            key + '=' + value for key, value in arg.items())

        where = ' WHERE id = %s' % id
        sql = ''.join(["UPDATE `%s` " % table, a, where])
        self.cursor.execute(sql)

    def remove(self, table=None, id=None):
        """Receives a table and ID and remove it"""
        if id and table:
            self.cursor.execute(
                "DELETE FROM `%s` WHERE `id` = %s" % (table, id))

    def insert(self, table=None, **kwargs):
        """Insert data in to the DB, receives a table and the
           data namecolumn=datatostore"""
        for key, value in kwargs.items():
            a = "(%s" % ', '.join(
                "`%s`" % key for key, value in kwargs.items()) + ')'
            b = "(%s" % ', '.join(
                "'%s'" % value for key, value in kwargs.items()) + ')'
        sql = "INSERT INTO `%s` " % table + a + ' VALUES ' + b
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False

    def disconnect(self):
        """Close the connection with the database"""
        self.cursor.close()
        self.db.close()
