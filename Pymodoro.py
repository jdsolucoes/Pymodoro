#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-
import time, pygtk, os, pango, gobject

from modules.db import db
from modules.playback import play
try:
    import pynotify
    notify = True
except:
    print "Pynotify was not found, disabling it."
    notify = None

pygtk.require('2.0')

import gtk
from gtk import glade



class main:
    
    def __init__(self):
        
        #define the alarms wav files
        
        self.alarms = {
            '2minutes' : 'files/sound/2minuteswarning.wav',
            'inicio' : 'files/sound/inicio.wav',
            'alarm' : 'files/sound/alarm.wav',
            'pausacurta' : 'files/sound/5minutos.wav',
            'pausalonga' : 'files/sound/pausalonga.wav'
        }
        
        #the default time in seconds, 25*60=1500 + 1
        self.time_seconds = 15
        #half break (or 5 minutes break) 300s + 1
        self.half_break_time = 301
        self.full_break_time = 901
        
        #set pomodoros, if it gets to FOUR enables the full_break_time
        self.pomodoros = 0
        self.time_break = False
        self.full_break = False
        self.thread_pid = 0
        #show or not the tasks tagged as done
        self.show_done_tasks = True
        
        #POG, but works
        self.lock_notify = None
        self.filesDir = os.path.abspath('files')
        self.w_gui = glade.XML("%s/gui/main.glade" % self.filesDir)
        self.main_window = self.w_gui.get_widget('janelaPrincipal')
        
        #here we defined the label that wiill show the time
        self.label_clock = self.w_gui.get_widget('labelClock')
        
        #big fat ass font.
        self.label_clock.modify_font(pango.FontDescription("35"))
        self.label_clock.set_padding(10, 5)
        self.main_window.show()
        
        
        #the list itself.
        self.list_tasks = gtk.ListStore(int,str,str,int,str)
        self.tree_tasks = self.w_gui.get_widget('listaTarefas')
        self.tree_tasks.set_model(self.list_tasks)
        
        
        cell = gtk.CellRendererText()
        task_column = gtk.TreeViewColumn('Tarefa:')
        task_column.pack_start(cell,True)
        task_column.add_attribute(cell,'text',2)
        
        
        self.tree_tasks.append_column(task_column)

        #systray icon
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("activate", self.activate)
        self.staticon.set_from_file("files/img/pomodoro.png")
        self.staticon.set_tooltip("pomodoro - Clique para Mostrar/Esconder")
        
        self.populateTaskList()
        
        self.staticon.set_visible(True) 
        
        #connecting the signals from GLADE/GTK to functions in python.
        signals = {
            'on_listaTarefas_cursor_changed' : self.updateInfo,
            'on_esconderMenu_activate' : self.hideDoneTasks,
            'on_finalizarMenu_activate' : self.setTaskDone,
            'on_deleteMenu_activate' : self.excluirTarefa,
            'on_imagemenuitem5_activate' : gtk.main_quit,
            'on_janelaPrincipal_destroy' : gtk.main_quit,
            'on_startBotao_clicked' : self.startTimer,
            'on_stopBotao_clicked' : self.stopTimer,
            'on_calendario_day_selected' : self.populateTaskList,
            'on_addBotao_clicked' : self.addTarefa
            
        }
        self.w_gui.signal_autoconnect(signals)
    
    
    def addTarefa(self,obj=None):
        
        """Get the name of the task from a GTK.entry
        and calls db().newTask()"""
        
        tt = self.w_gui.get_widget("nomeEntrada")
        nome = tt.get_text()
        tt.set_text('')
        
        db().newTask(nome)
        self.populateTaskList()
        
        return None
    
    def excluirTarefa(self, obj=None):
        
        
        
        model, iter = self.tree_tasks.get_selection().get_selected()
        
        if model and iter:
            
            id = model.get_value(iter,0)
            db().removeTask(id)
            self.populateTaskList()
            
            return True
        else:
            return None
            
    def setTaskDone(self,obj=None):
        
        model, iter = self.tree_tasks.get_selection().get_selected()
        
        if model and iter:
            
            id = model.get_value(iter,0)
            db().update('tarefas',id,concluido='Sim')
            self.populateTaskList()
            
    def markDays (self,obj=None):
        
        calendario = self.w_gui.get_widget('calendario')
        calendario.clear_marks()
        year, month, day = calendario.get_date()
        month += 1
        dias = db().getByDate(None,month)
        for i in dias:
            calendario.mark_day(i[4].day)
        
        
    def populateTaskList(self,obj=None):
        cc = self.w_gui.get_widget('calendario')
        
        year, month, day = cc.get_date()
        month = month + 1
        tasks = db().getListOfTasks(day,month,year)
        
        
        for i in self.list_tasks:
            
            self.list_tasks.remove(i.iter)
        if self.show_done_tasks:
            for i in tasks:
                self.list_tasks.append(i)
                
        else:
            
            for i in tasks:
                
                if i[1] == 'Sim':
                    pass
                else:
                    self.list_tasks.append(i)
        self.markDays()            
        
        
        
    
    def startTimer(self, *args):
        model, iter = self.tree_tasks.get_selection().get_selected()
           
        if self.time_break:
            
            if self.full_break:
                self.full_break = False
                self.startTime = time.time() + self.full_break_time
            else:
                self.time_break = False
                self.startTime = time.time() + self.half_break_time
                
            self.thread_pid = gobject.timeout_add(10,self.run)
            
        else:   
            if self.thread_pid == 0 and model and iter:
                self.alarm(self.alarms['inicio'])
                self.lock_notify = None
                self.idAtivo = model.get_value(iter,0)
                self.startTime = time.time() + self.time_seconds
                self.thread_pid = gobject.timeout_add(10,self.run)
                self.changeIcon('Normal',True)
            
            
    def activate(self,obj):
        
        if (self.main_window.flags() & gtk.VISIBLE) != 0:
            
            self.main_window.hide()
        else:
            self.main_window.show()
            
            
    def alarm(self,file=None):
        
        if file:
            
            d = play(file)
        
    def updateInfo(self,obj):
        
        model, iter = obj.get_selection().get_selected()
        
        if iter:
            
            data = model.get_value(iter,4)
            pomodoros = model.get_value(iter,3)
            status = model.get_value(iter,1)
            self.w_gui.get_widget('labelData').set_text(data)
            self.w_gui.get_widget('labelPomodoros').set_text(str(pomodoros))
            self.w_gui.get_widget('labelStatus').set_text(status)
        
    def stopTimer(self, obj=None):

        if self.thread_pid != 0:
            self.lock_notify = False
            if obj:
                self.time_break = False
            self.changeIcon('Normal')
            gobject.source_remove(self.thread_pid)
            self.label_clock.set_text("00:00")
            self.startTime = time.time()
            self.thread_pid = 0
            
            

    def notifyIt(self,msg=None):
        
        if notify and msg:
            if pynotify.init('Pymodoro'):
                
                n = pynotify.Notification('pomodoro', msg,'files/img/pomodoro.png')
                n.attach_to_status_icon(self.staticon)
                n.show()
                
                return True
        else:
            
            return None
                
    def changeIcon(self,icon=None,blinking=None):
        
        if icon:
            if icon == 'Normal':
                self.staticon.set_from_file("files/img/pomodoro.png")
                
            elif icon == 'Break':
                self.staticon.set_from_file("files/img/pomodoro-break.png")
                
            else:
                return None
            
            if blinking:
                
                self.staticon.set_blinking(True)
            
            else:
                self.staticon.set_blinking(False)
                
            return True
        
    def finished(self):
        
        
        """Here we define what will happen when the clocks hits 0"""
        
        
        self.stopTimer()
        self.lock_notify = False
        
        
        if self.time_break:
            
            if self.pomodoros > 3:
                self.full_break = True
                self.pomodoros = 0
            else:
                self.pomodoros += 1
                
            
            self.changeIcon('Normal')
            self.notifyIt('Descanso Acabou, volta a trabalhar vagabundo!')
            self.alarm(self.alarms['alarm'])
            
            self.time_break = False
        else:
            
            pomodoros = db().getPomodoros(self.idAtivo) + 1
            self.w_gui.get_widget('labelPomodoros').set_text(str(pomodoros))
            db().update('tarefas',self.idAtivo,pomodoros=pomodoros)
            self.pomodoros = self.pomodoros + 1
            
            self.changeIcon('Break',True)
            self.notifyIt('Iniciando pausa... 5 minutos, corre negada!.')
            self.alarm(self.alarms['pausacurta'])
            self.time_break = True
            self.startTimer()
        
    
    def hideDoneTasks(self,obj=None):
        
        if self.show_done_tasks == False:
            self.show_done_tasks = True
        else:
            self.show_done_tasks = False
        
        self.populateTaskList()

    
    def run(self):   
        
        diff_time =  self.startTime - time.time()
        (minutes, seconds) = divmod(diff_time, 60.0)
        
        if int(diff_time) == 0:
            
            self.finished()
            return False
    
        else:
        
            self.label_clock.set_text("%02i:%02i" % (minutes,seconds))
        
        if int(diff_time) < 120:
            
            if self.lock_notify:
                pass
            else:
                if self.time_break:
                    self.lock_notify = True
                else:
                    self.notifyIt('Faltam apenas 2 minutos')
                    self.alarm(self.alarms['2minutes'])
                    self.lock_notify = True
        
        
        return True
        
app = main()
gtk.main()