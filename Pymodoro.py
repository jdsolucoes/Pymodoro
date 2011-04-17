#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-
import time, pygtk, os, pango, gobject

from modules import db

try:
    import pynotify
    notify = True
except:
    print "Pynotify não encontrado... desabilitando"
    notify = None

pygtk.require('2.0')

import gtk
from gtk import glade



class main:
    
    def __init__(self):
        #tempo a regressar em segundos (padrão 25 minutos) + 1
        self.tempoSegundos = 1501
        self.rolling = 0
        
        
        
        self.filesDir = os.path.abspath('files')
        self.wGui = glade.XML("%s/gui/main.glade" % self.filesDir)
        self.mainWindow = self.wGui.get_widget('janelaPrincipal')
        self.labelClock = self.wGui.get_widget('labelClock')
        self.labelClock.modify_font(pango.FontDescription("27"))
        self.labelClock.set_padding(10, 5)
        self.mainWindow.show()
        
        
        #iniciando visualização de tarefas
        
        self.listaTarefas = gtk.ListStore(int,str,int,str)
        self.treeTarefas = self.wGui.get_widget('listaTarefas')
        self.treeTarefas.set_model(self.listaTarefas)
        #colunas
        
        
        cell = gtk.CellRendererText()
        
        #pegando campos da tabela tarefas
        campos = db.db().get_campos()
        #iniciando contador
        n = 0
        #loop em todos os itens
        dict = {}
        for i in campos:
            
            #primeira maiuscula....
            x = i[0].capitalize()
            
            
            dict[x] = gtk.TreeViewColumn(x)
            dict[x].pack_start(cell,True)
            dict[x].add_attribute(cell,'text',n)
            self.treeTarefas.append_column(dict[x])
            
            n = n + 1
            

        
        
        #gerando icone de status....
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("activate", self.activate)
        self.staticon.set_from_file("%s/img/pomodoro.png" % self.filesDir) 
        
        self.popularLista()
        
        self.staticon.set_visible(True) 
        
        
        signals = {
            'on_janelaPrincipal_destroy' : gtk.main_quit,
            'on_startBotao_clicked' : self.startTimer,
            'on_stopBotao_clicked' : self.stopTimer,
            'on_calendario_day_selected' : self.popularLista,
            'on_addBotao_clicked' : self.addTarefa
            
        }
        self.wGui.signal_autoconnect(signals)
    

    
    def addTarefa(self,obj=None):
        
        tt = self.wGui.get_widget("nomeEntrada").get_text()
        db.db().insert_tarefa(tt)
        self.popularLista()

    
    def popularLista(self,obj=None):
        cc = self.wGui.get_widget('calendario')
        
        year, month, day = cc.get_date()
        month = month + 1
        tarefas = db.db().get_lista_tarefas(day,month,year)

        
        for i in self.listaTarefas:
            
            self.listaTarefas.remove(i.iter)
        for i in tarefas:
            self.listaTarefas.append(i)
            pass
        
        
        
    
    def startTimer(self, *args):
        
        if self.rolling == 0:
            self.startTime = time.time() + self.tempoSegundos
            self.rolling = gobject.timeout_add(10,self.contar)
            self.staticon.set_blinking(True)
            
            
    def activate(self,obj):
        if (self.mainWindow.flags() & gtk.VISIBLE) != 0:
            
            self.mainWindow.hide()
        else:
            self.mainWindow.show()
            
            
        
    def stopTimer(self, obj=None):
        
        if obj:
            
            self.tempoSegundos = 1500
        
        if self.rolling != 0:
            
            gobject.source_remove(self.rolling)
            self.labelClock.set_text("00:00")
            self.startTime = time.time()
            self.rolling = 0
            self.staticon.set_blinking(False) 
            
            
    def alarm(self):
        
        self.notificar('Acabou o Tempo Negadis')
        self.stopTimer()
    
        
            
        self.mainWindow.show()
        
    
    def notificar(self,msg=None):
        if notify and msg:
            if pynotify.init('Pomodoro'):
                
                n = pynotify.Notification('Pomodoro', msg)
                n.attach_to_status_icon(self.staticon)
                n.show()
                
    
    def contar(self):   
        
        diferenca =  self.startTime - time.time()
        (minutoss, segundos) = divmod(diferenca, 60.0)
        
        if int(diferenca) == 0:
            
            self.alarm()
            return False
        else:
        
            self.labelClock.set_text("%02i:%02i" % (minutoss,segundos))
        
        return True
        
app = main()
gtk.main()