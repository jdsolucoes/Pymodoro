#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

import MySQLdb


class db:
    
    def connect(self):
        
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
        
    def get_all(self,tabela=None, **kwarg):
        
        if tabela:
            chave = kwarg.keys()[0]
            valor = kwarg[chave]
            sql = "SELECT * FROM `%s` WHERE %s = '%s'" % (tabela,chave,valor)
            
            self.cursor.execute(sql)
            
            return self.cursor.fetchall()
    
    def get_by_date(self,day=None,month=None,year=None):
        
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

        #self.cursor.execute(sql)
        

        self.cursor.execute(sql)
        return self.cursor.fetchall()
        
    def update(self,tabela=None,id=None,**kwargs):
        
        arg = {}
        arg.update(kwargs)

        for key, value in arg.items():
            arg[key] = (str(value), repr(value))[type(value) == str]
        a = 'SET %s' % ', '.join(key + '=' + value for key, value in arg.items())

        where = ' WHERE id = %s' % id

        sql = ''.join(["UPDATE `%s` " % tabela,a,where])
        self.cursor.execute(sql)
    
    def remove(self,tabela=None,id=None):
        
        if id and tabela:
            
            self.cursor.execute("DELETE FROM `%s` WHERE `id` = %s" % (tabela,id))
            
                
            
    def insert(self,tabela=None,**kwargs):
        
        for key,value in kwargs.items():
            
            a = "(%s" % ', '.join("`%s`" % key  for key, value in kwargs.items()) + ')'
            b = "(%s" % ', '.join("'%s'" % value for key,value in kwargs.items()) + ')'
        
        sql = "INSERT INTO `%s` " % tabela + a + ' VALUES ' + b
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False
        
        
    def disconnect(self):
        
        """Fechamos a conexão com o Banco de Dados"""
        
        self.cursor.close()
        self.db.close()
        
        
    def select_from(self,*args):
        
        pass
        
        