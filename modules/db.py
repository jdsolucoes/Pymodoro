#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

import config
from datetime import datetime

try:
    exec("from %s import db as backend" % config.db_config['backend'])
except:
    print "Erro eo importar modulo %s\n" % config.db_config['backend']
    exit(1)
    

class db(backend):
    
    
    def __init__(self):
        
        
        self.db_config = config.db_config
        if not self.connect():
            exit('Erro ao conectar ao DB')
        
    def getFields(self):
        
        self.cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tarefas'")
        return self.cursor.fetchall()
        
    def getListOfTasks(self,day,month,year):
        
        if day and month and year:
            
            return self.getByDate(day,month,year)
            
        else:
            return none
    
    def removeTask(self,id=None):
        
        if id:
            self.remove('tarefas',id)
            
    
    def newTask(self,tarefa=None):
        
        if tarefa:
            
            self.insert('tarefas',concluido="Nao",tarefa=tarefa,data=datetime.now(),pomodoros=0)
        
            
    def updatePomodoro(self,id=None,pomodoro=None):
        if id and pomodoro:
            self.update('tarefas',id,pomodoros=pomodoro)
    
    def __del__(self):
        
        self.disconnect()
            
            
