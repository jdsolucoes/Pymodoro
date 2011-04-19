#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-
import time, pygtk, os, pango, gobject

from modules import db
from modules.playback import play
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
        
        #definir os alarmes...
        
        self.alarms = {
            '2minutes' : 'files/sound/2minuteswarning.wav',
            'inicio' : 'files/sound/inicio.wav',
            'alarm' : 'files/sound/alarm.wav',
            'pausacurta' : 'files/sound/5minutos.wav',
            'pausalonga' : 'files/sound/pausalonga.wav'
        }
        
        #tempo a regressar em segundos (padrão 25 minutos) + 1
        self.tempoSegundos = 1501
        self.tempoBreak = 301
        self.tempoBreakLongo = 901
        self.Pomodoros = 0
        self.descanso = False
        self.rolling = 0
        
        
        self.mostrarConcluidos = True
        self.lockNotify = None
        self.filesDir = os.path.abspath('files')
        self.wGui = glade.XML("%s/gui/main.glade" % self.filesDir)
        self.mainWindow = self.wGui.get_widget('janelaPrincipal')
        
        #aqui definimos o label que sera responsavel por mostrar o tempo
        self.labelClock = self.wGui.get_widget('labelClock')
        
        #aumentamos a fonte
        self.labelClock.modify_font(pango.FontDescription("35"))
        self.labelClock.set_padding(10, 5)
        self.mainWindow.show()
        
        
        #iniciando visualização de tarefas
        
        self.listaTarefas = gtk.ListStore(int,str,str,int,str)
        self.treeTarefas = self.wGui.get_widget('listaTarefas')
        self.treeTarefas.set_model(self.listaTarefas)
        
        #colunas
        
        
        cell = gtk.CellRendererText()
        
        tarefaColumn = gtk.TreeViewColumn('Tarefa:')
        tarefaColumn.pack_start(cell,True)
        tarefaColumn.add_attribute(cell,'text',2)
        
        
        self.treeTarefas.append_column(tarefaColumn)

        #gerando icone de status....
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("activate", self.activate)
        self.staticon.set_from_file("files/img/pomodoro.png")
        self.staticon.set_tooltip("Pomodoro - Clique para Mostrar/Esconder")
        
        self.popularLista()
        
        self.staticon.set_visible(True) 
        
        
        signals = {
            'on_listaTarefas_cursor_changed' : self.updateInformacoes,
            'on_esconderMenu_activate' : self.esconderConcluidos,
            'on_finalizarMenu_activate' : self.finalizarTarefa,
            'on_deleteMenu_activate' : self.excluirTarefa,
            'on_janelaPrincipal_destroy' : gtk.main_quit,
            'on_startBotao_clicked' : self.startTimer,
            'on_stopBotao_clicked' : self.stopTimer,
            'on_calendario_day_selected' : self.popularLista,
            'on_addBotao_clicked' : self.addTarefa
            
        }
        self.wGui.signal_autoconnect(signals)
    
    
    def addTarefa(self,obj=None):
        
        tt = self.wGui.get_widget("nomeEntrada")
        nome = tt.get_text()
        tt.set_text('')
        
        db.db().insert_tarefa(nome)
        self.popularLista()
    
    def excluirTarefa(self, obj=None):
        
        model, iter = self.treeTarefas.get_selection().get_selected()
        
        if model and iter:
            
            id = model.get_value(iter,0)
            db.db().remove_tarefa(id)
            self.popularLista()
            
    def finalizarTarefa(self,obj=None):
        
        model, iter = self.treeTarefas.get_selection().get_selected()
        
        if model and iter:
            
            id = model.get_value(iter,0)
            db.db().update('tarefas',id,concluido='Sim')
            self.popularLista()
            
    def marcarDias (self,obj=None):
        
        calendario = self.wGui.get_widget('calendario')
        calendario.clear_marks()
        year, month, day = calendario.get_date()
        month += 1
        dias = db.db().get_by_date(None,month)
        for i in dias:
            calendario.mark_day(i[4].day)
        
        
    def popularLista(self,obj=None):
        cc = self.wGui.get_widget('calendario')
        
        year, month, day = cc.get_date()
        month = month + 1
        tarefas = db.db().get_lista_tarefas(day,month,year)

        
        for i in self.listaTarefas:
            
            self.listaTarefas.remove(i.iter)
        if self.mostrarConcluidos:
            for i in tarefas:
                self.listaTarefas.append(i)
                
        else:
            
            for i in tarefas:
                
                if i[1] == 'Sim':
                    pass
                else:
                    self.listaTarefas.append(i)
        self.marcarDias()            
        
        
        
    
    def startTimer(self, *args):
        model, iter = self.treeTarefas.get_selection().get_selected()
           
        if self.descanso:
            
            if self.Pomodoros > 3:
                self.Pomodoros = 0
                self.startTime = time.time() + self.tempoBreakLongo
            else:
                
                self.startTime = time.time() + self.tempoBreak
                
            
            
            self.rolling = gobject.timeout_add(10,self.contar)
        else:   
            if self.rolling == 0 and model and iter:
                self.alarm(self.alarms['inicio'])
                self.lockNotify = None
                self.idAtivo = model.get_value(iter,0)
                self.startTime = time.time() + self.tempoSegundos
                self.rolling = gobject.timeout_add(10,self.contar)
                self.staticon.set_blinking(True)
            
            
    def activate(self,obj):
        if (self.mainWindow.flags() & gtk.VISIBLE) != 0:
            
            self.mainWindow.hide()
        else:
            self.mainWindow.show()
            
            
    def alarm(self,file=None):
        
        if file:
            
            d = play(file)
        
    def updateInformacoes(self,obj):
        
        model, iter = obj.get_selection().get_selected()
        
        if iter:
            
            data = model.get_value(iter,4)
            pomodoros = model.get_value(iter,3)
            status = model.get_value(iter,1)
            self.wGui.get_widget('labelData').set_text(data)
            self.wGui.get_widget('labelPomodoros').set_text(str(pomodoros))
            self.wGui.get_widget('labelStatus').set_text(status)
        
    def stopTimer(self, obj=None):

        if self.rolling != 0:
            self.lockNotify = False
            if obj:
                self.descanso = False
            self.staticon.set_from_file("files/img/pomodoro.png")
            gobject.source_remove(self.rolling)
            self.labelClock.set_text("00:00")
            self.startTime = time.time()
            self.rolling = 0
            self.staticon.set_blinking(False) 
            

    def notificar(self,msg=None):
        if notify and msg:
            if pynotify.init('Pomodoro'):
                
                n = pynotify.Notification('Pomodoro', msg,'files/img/pomodoro.png')
                n.attach_to_status_icon(self.staticon)
                n.show()
                
    
    def finalizou(self):
        
        self.stopTimer()
        self.lockNotify = False
        pomodoros = db.db().get_all('tarefas',id=self.idAtivo)[0][3] + 1
        if not self.descanso:
            db.db().update('tarefas',self.idAtivo,pomodoros=pomodoros)
            self.Pomodoros = self.Pomodoros + 1
            self.popularLista()
        
        if self.descanso:
            
            
            self.staticon.set_from_file("files/img/pomodoro.png")
            self.notificar('Descanso Acabou, volta a trabalhar vagabundo!')
            self.alarm(self.alarms['alarm'])
            
            self.descanso = False
        else:
            
            self.staticon.set_from_file("files/img/pomodoro-break.png")
            self.notificar('Iniciando pausa... 5 minutos, corre negada!.')
            self.alarm(self.alarms['pausacurta'])
            self.staticon.set_blinking(True) 
            self.descanso = True
            self.startTimer()
        
    
    def esconderConcluidos(self,obj=None):
        
        if self.mostrarConcluidos == False:
            self.mostrarConcluidos = True
        else:
            self.mostrarConcluidos = False
        
        self.popularLista()

    
    def contar(self):   
        
        diferenca =  self.startTime - time.time()
        (minutoss, segundos) = divmod(diferenca, 60.0)
        
        if int(diferenca) == 0:
            
            self.finalizou()
            return False
    
        else:
        
            self.labelClock.set_text("%02i:%02i" % (minutoss,segundos))
        
        if int(diferenca) < 120:
            if self.lockNotify:
                pass
            else:
                if self.descanso:
                    self.lockNotify = True
                else:
                    self.notificar('Faltam apenas 2 minutos')
                    self.alarm(self.alarms['2minutes'])
                    self.lockNotify = True
        
        
        return True
        
app = main()
gtk.main()