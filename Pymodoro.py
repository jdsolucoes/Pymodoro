#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-
import time, pygtk, os, pango, gobject

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
        self.tempoSegundos = 16
        self.rolling = 0
        
        
        
        self.filesDir = os.path.abspath('files')
        self.wGui = glade.XML("%s/gui/main.glade" % self.filesDir)
        self.mainWindow = self.wGui.get_widget('janelaPrincipal')
        self.labelClock = self.wGui.get_widget('labelClock')
        self.labelClock.modify_font(pango.FontDescription("27"))
        self.labelClock.set_padding(10, 5)
        self.mainWindow.show()
        
        
        #iniciando visualização de tarefas
        
        self.listaTarefas = gtk.ListStore(int,str,int)
        self.treeTarefas = self.wGui.get_widget('listaTarefas')
        self.treeTarefas.set_model(self.listaTarefas)
        #colunas
        
        
        cell = gtk.CellRendererText()
        
        id_colum = gtk.TreeViewColumn('ID:')
        nome_colum = gtk.TreeViewColumn('Tarefa:')
        pomodoro_colum = gtk.TreeViewColumn('Pomodoros:')
        
        id_colum.pack_start(cell,True)
        id_colum.add_attribute(cell,'text',0)
        
        nome_colum.pack_start(cell,True)
        nome_colum.add_attribute(cell,'text',1)
        
        pomodoro_colum.pack_start(cell,True)
        pomodoro_colum.add_attribute(cell,'text',2)
        
        
        
        self.treeTarefas.append_column(id_colum)
        self.treeTarefas.append_column(nome_colum)
        self.treeTarefas.append_column(pomodoro_colum)
        
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("activate", self.activate)
        self.staticon.set_from_file("%s/img/pomodoro.png" % self.filesDir) 
        
        
        
        self.staticon.set_visible(True) 
        
        
        signals = {
            'on_janelaPrincipal_destroy' : gtk.main_quit,
            'on_startBotao_clicked' : self.startTimer,
            'on_stopBotao_clicked' : self.stopTimer
            
        }
        self.wGui.signal_autoconnect(signals)
        
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