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


import time
import pygtk
import os
import pango
import gobject

from modules.db import db
from modules.playback import play
import datetime


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
        self.time_seconds = 1501

        #half break (or 5 minutes break) 300s + 1
        self.half_break_time = 301
        self.full_break_time = 901

        #set pomodoros, if it gets to FOUR enables the full_break_time
        self.pomodoros = 0
        self.active_break = False
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
        self.list_tasks = gtk.ListStore(int,int,str,int,str)
        self.tree_tasks = self.w_gui.get_widget('listaTarefas')
        self.tree_tasks.set_model(self.list_tasks)
        self.tree_tasks.connect('button_press_event',self.menuPopup)
        self.tree_tasks.set_search_column(2)        
        cell = gtk.CellRendererText()
        cell.set_property('strikethrough' , True)
        task_column = gtk.TreeViewColumn('Tarefa:')
        task_column.pack_start(cell,True)
        task_column.add_attribute(cell,'text',2)
        task_column.set_attributes(cell,text=2,strikethrough=1)
        self.tree_tasks.append_column(task_column)
        
        #systray icon
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("button_press_event", self.activate)
        self.staticon.set_from_file("files/img/pomodoro.png")
        self.staticon.set_tooltip("Pymodoro - Clique para Mostrar/Esconder")
        self.staticon.set_visible(True)
        
        #call populateTaskList()
        self.populateTaskList()
        
        #connecting the signals from GLADE/GTK to functions in python.
        signals = {
            'on_listaTarefas_cursor_changed' : self.updateInfo,
            'on_esconderMenu_activate' : self.hideDoneTasks,
            'on_finalizarMenu_activate' : self.setTaskDone,
            'on_deleteMenu_activate' : self.deleteTask,
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
        if nome != '':
            db().newTask(nome)
            self.notifyIt("Tarefa: '%s' Adicionada." % nome)
            self.populateTaskList()
            tt.set_text('')
        else:
            self.notifyIt('Nome de Tarefa Inválido')
        
        return None
    
    
    def deleteTask(self, obj=None):
        
        """
        Get the current selected task and remove it
        """
        
        model, iter = self.tree_tasks.get_selection().get_selected()
        
        if model and iter:
            
            id = model.get_value(iter,0)
            db().removeTask(id)
            self.populateTaskList()
            
            return True
        else:
            return None
        
            
    def setTaskDone(self,obj=None):
        
        """
        Set the current task as done/todo
        """
        
        model, iter = self.tree_tasks.get_selection().get_selected()
        
        if model and iter:
            
            id = model.get_value(iter,0)
            fineshed = model.get_value(iter,1)
            if fineshed == 1:
                db().update('tarefas',id,concluido=0)
            else:
                db().update('tarefas',id,concluido=1)
            self.populateTaskList()
            
            
    def menuPopup(self,obj, event):

        """
        menuPopup, shows the menu for the treeview
        """
        
        #if the mouse button isn't the Right button...pass
        if event.button != 3:
            pass
        else:
            
            #getting the selected path
            path = obj.get_path_at_pos(int(event.x),int(event.y))
            #getting the selection object from obj
            selection = obj.get_selection()
            #getting the current selected rows,
            #in this case it can't be higher than one
            selected = selection.get_selected_rows()
            #if path dosen't exist, return None
            if not path:
                return None
            #if the path is not selected than select it.
            if path[0] not in selected[1]:
                selection.unselect_all()
                selection.select_path(path[0])
            #again if the count returns more than one IT WILL FAIL.
            if selection.count_selected_rows() > 1:
                pass
            #if not show the menu
            else:
                model, iter = selection.get_selected()
                #get the current status of the task(done or to do);
                done = model.get_value(iter,1)
                m = gtk.Menu()
                r_task = gtk.MenuItem("Remover Tarefa")
                #if done is equal to one it means that the task is done
                if done == 1:
                    #show this then
                    m_done = gtk.MenuItem("Desmarcar como feita")
                else:
                    #if not show this
                    m_done = gtk.MenuItem("Marcar como feita")
                    
            #connecting the events.
            m_done.connect('activate',self.setTaskDone)
            r_task.connect('activate',self.deleteTask)
            
            #showing all!
            r_task.show()
            m_done.show()
            
            #appending the menu itens
            m.append(m_done)
            m.append(r_task)
            
            #poping it up.
            m.popup(None, None, None, event.button, event.time, None)
            return False
        
        
    def markDays (self,obj=None):
        
        """
        Get all days that have tasks within and mark them on the calendar
        """
        
        calendario = self.w_gui.get_widget('calendario')
        calendario.clear_marks()
        year, month, day = calendario.get_date()
        month += 1
        dias = db().getByDate(None,month)
        for i in dias:
            calendario.mark_day(i[4].day)
            
            
    def populateTaskList(self,obj=None):
        
        """
        Populate the taks list
        and then calls self.markDays()
        """
        
        cc = self.w_gui.get_widget('calendario')
        year, month, day = cc.get_date()
        #the gtk calendar aways return the month wrong, adding 1... POG?
        month = month + 1
        tasks = db().getListOfTasks(day,month,year)
        
        #remove all items on the list
        for i in self.list_tasks:
            self.list_tasks.remove(i.iter)
            
        #append new ones.
        for i in tasks:
            if not self.show_done_tasks and i[1] ==1:
                pass
            else:
                self.list_tasks.append(i)
        self.markDays()
        
        
    def startTimer(self, *args):
        
        """
        Start the fucking timer....
        """

        model, iter = self.tree_tasks.get_selection().get_selected()
           
        if self.active_break:    
            if self.full_break:
                self.full_break = False
                self.startTime = time.time() + self.full_break_time
            else:
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
                
                
    def activate(self,obj,event):
        
        """Stupid ass name, i know, shame on me"""
        
        if event.button == 3:
            self.stopTimer()
        else:
            if (self.main_window.flags() & gtk.VISIBLE) != 0:    
                self.main_window.hide()
            else:
                self.main_window.show()
            

    def alarm(self,file=None):
        
        """Play a sound file"""
        
        if file:            
            play().play(file)
            
        
    def updateInfo(self,obj):
        
        """Get the Info from the list and then update the
        labels, date, pomodoros etc...
        """
        
        model, iter = obj.get_selection().get_selected()
        if iter:
            id = model.get_value(iter,0)
            row = db().getByID(id)
            data = datetime.datetime.strftime(row[4],'%d/%m/%Y')
            self.w_gui.get_widget('labelData').set_text(data)
            self.w_gui.get_widget('labelPomodoros').set_text(str(row[3]))
            status = row[1]
            
            if status == 1:
                self.w_gui.get_widget('labelStatus').set_text('Sim')
            else:
                self.w_gui.get_widget('labelStatus').set_text('Não')
                

    def stopTimer(self, obj=None):

        """Stop the timer"""
        
        if self.thread_pid != 0:
            self.lock_notify = False
            if obj:
                self.active_break = False
            self.changeIcon('Normal')
            gobject.source_remove(self.thread_pid)
            self.label_clock.set_text("00:00")
            self.startTime = time.time()
            self.thread_pid = 0
            

    def notifyIt(self,msg=None):
        
        """Use pynotify to emit a notification, looks great in ubuntu"""
        
        if notify and msg:
            if pynotify.init('Pymodoro'):                
                n = pynotify.Notification('Pymodoro', msg,'files/img/pomodoro.png')
                n.attach_to_status_icon(self.staticon)
                n.show()
                
                return True
        else:
            return None
                
    def changeIcon(self,icon=None,blinking=None):
        
        """Use the change the status of the icon, blinking or not, Normal or
        break time"""
        
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
        
        if self.active_break:
            if self.pomodoros > 3:
                self.full_break = True
                self.pomodoros = 0
            else:
                self.pomodoros += 1    
            self.changeIcon('Normal')
            self.alarm(self.alarms['alarm'])
            self.notifyIt('Descanso Acabou, volta a trabalhar vagabundo!')
            self.active_break = False
        else:
            pomodoros = db().getPomodoros(self.idAtivo) + 1
            self.w_gui.get_widget('labelPomodoros').set_text(str(pomodoros))
            db().update('tarefas',self.idAtivo,pomodoros=pomodoros)
            self.pomodoros = self.pomodoros + 1
            self.changeIcon('Break',True)
            self.notifyIt('Iniciando pausa... 5 minutos, corre negada!.')
            self.alarm(self.alarms['pausacurta'])
            self.active_break = True
            self.startTimer()
            
            
    def hideDoneTasks(self,obj=None):
        
        """Hidden the tasks tagged as done"""
        
        if self.show_done_tasks == False:
            self.show_done_tasks = True
        else:
            self.show_done_tasks = False
        self.populateTaskList()

    
    def run(self):   
        
        """the function that holds the clock itself"""
        
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
                if self.active_break:
                    self.lock_notify = True
                else:
                    self.notifyIt('Faltam apenas 2 minutos')
                    self.alarm(self.alarms['2minutes'])
                    self.lock_notify = True
        return True


app = main()
gtk.gdk.threads_init
gtk.main()
