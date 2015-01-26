#!/usr/bin/env python
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

    def getListOfTasks(self, day, month, year):
        """Return a list of tasks"""
        if day and month and year:
            return self.getByDate(day,month,year)
        else:
            return none

    def removeTask(self,id=None):
        """"Remove a task"""
        if id:
            self.remove('tarefas',id)

    def newTask(self, tarefa=None):
        """Create a new Task"""
        if tarefa:
            self.insert(
                'tarefas', concluido=0, tarefa=tarefa,
                data=datetime.now(), pomodoros=0)

    def getPomodoros(self, id=None):
        """Return the amount of pomodoros of that task"""
        if id:
            c = self.getAll('tarefas',id=id)[0][3]
            return c
        else:
            return None

    def updatePomodoro(self,id=None,pomodoro=None):
        """Update the amount of pomodoros of a task"""
        if id and pomodoro:
            self.update('tarefas',id,pomodoros=pomodoro)

    def __del__(self):
        self.disconnect()
