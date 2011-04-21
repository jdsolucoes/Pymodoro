#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-


class AbstractSQL:
        
    def getAll(self,table=None, **kwarg):
        
        if table:
            key = kwarg.keys()[0]
            valor = kwarg[key]
            sql = "SELECT * FROM `%s` WHERE %s = '%s'" % (table,key,valor)
            
            self.cursor.execute(sql)
            
            return self.cursor.fetchall()
    
    def getByDate(self,day=None,month=None,year=None):
        
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
        
    def update(self,table=None,id=None,**kwargs):
        
        arg = {}
        arg.update(kwargs)

        for key, value in arg.items():
            arg[key] = (str(value), repr(value))[type(value) == str]
        a = 'SET %s' % ', '.join(key + '=' + value for key, value in arg.items())

        where = ' WHERE id = %s' % id

        sql = ''.join(["UPDATE `%s` " % table,a,where])
        self.cursor.execute(sql)
    
    def remove(self,table=None,id=None):
        
        if id and table:
            
            self.cursor.execute("DELETE FROM `%s` WHERE `id` = %s" % (table,id))
            
                
            
    def insert(self,table=None,**kwargs):
        
        for key,value in kwargs.items():
            
            a = "(%s" % ', '.join("`%s`" % key  for key, value in kwargs.items()) + ')'
            b = "(%s" % ', '.join("'%s'" % value for key,value in kwargs.items()) + ')'
        
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
        
        

        
        