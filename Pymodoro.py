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

import time
import os
import gobject
import pygtk
import pango
import datetime

from modules.db import db
from modules.playback import play

import gtk
from gtk import glade
pygtk.require('2.0')


try:
    import pynotify
    notify = True
except ImportError:
    print "Pynotify was not found, disabling it."
    notify = None


class Pymodoro(object):

    alarms = {
        '2minutes': 'files/sound/2minuteswarning.wav',
        'inicio': 'files/sound/inicio.wav',
        'alarm': 'files/sound/alarm.wav',
        'pausacurta': 'files/sound/5minutos.wav',
        'pausalonga': 'files/sound/pausalonga.wav'
    }
    time_seconds = 1501
    half_break_time = 301
    full_break_time = 901
    pomodoros = 0
    active_break = False
    full_break = False
    thread_pid = 0

    def __init__(self):
        self.show_done_tasks = True
        self.lock_notify = None
        self.filesDir = os.path.realpath('files')
        self.w_gui = glade.XML("%s/gui/main.glade" % self.filesDir)
        self.main_window = self.w_gui.get_widget('janelaPrincipal')

        self.label_clock = self.w_gui.get_widget('labelClock')
        self.label_clock.modify_font(pango.FontDescription("35"))
        self.label_clock.set_padding(10, 5)
        self.main_window.show()

        # The list itself.
        self.list_tasks = gtk.ListStore(int, int, str, int, str)
        self.tree_tasks = self.w_gui.get_widget('listaTarefas')
        self.tree_tasks.set_model(self.list_tasks)
        self.tree_tasks.connect('button_press_event', self.menu_popup)
        self.tree_tasks.set_search_column(2)
        cell = gtk.CellRendererText()
        cell.set_property('strikethrough', True)
        task_column = gtk.TreeViewColumn('Tarefa:')
        task_column.pack_start(cell, True)
        task_column.add_attribute(cell, 'text', 2)
        task_column.set_attributes(cell, text=2, strikethrough=1)
        self.tree_tasks.append_column(task_column)

        # Systray icon
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("button_press_event", self.activate)
        self.staticon.set_from_file("files/img/pomodoro.png")
        self.staticon.set_tooltip("Pymodoro - Clique para Mostrar/Esconder")
        self.staticon.set_visible(True)

        # Call populate_task_list()
        self.populate_task_list()

        # Connecting the signals from GLADE/GTK to functions in python.
        signals = {
            'on_listaTarefas_cursor_changed': self.update_info,
            'on_esconderMenu_activate': self.hide_done_tasks,
            'on_finalizarMenu_activate': self.finish_task,
            'on_deleteMenu_activate': self.delete_task,
            'on_imagemenuitem5_activate': gtk.main_quit,
            'on_janelaPrincipal_destroy': gtk.main_quit,
            'on_startBotao_clicked': self.start_timer,
            'on_stopBotao_clicked': self.stop_timer,
            'on_calendario_day_selected': self.populate_task_list,
            'on_addBotao_clicked': self.add_tarefa
        }
        self.w_gui.signal_autoconnect(signals)

    def add_tarefa(self, obj=None):
        """Get the name of the task from a GTK.entry
        and calls db().newTask()"""
        tt = self.w_gui.get_widget("nomeEntrada")
        nome = tt.get_text()
        if nome != '':
            db().newTask(nome)
            self.notificate("Tarefa: '%s' Adicionada." % nome)
            self.populate_task_list()
            tt.set_text('')
        else:
            self.notificate('Nome de Tarefa Inválido')
        return None

    def delete_task(self, obj=None):
        """
        Get the current selected task and remove it
        """
        model, iter = self.tree_tasks.get_selection().get_selected()
        if model and iter:
            id = model.get_value(iter, 0)
            db().removeTask(id)
            self.populate_task_list()

            return True
        else:
            return None

    def finish_task(self, obj=None):
        """
        Set the current task as done/todo
        """
        model, iterator = self.tree_tasks.get_selection().get_selected()
        if model and iterator:
            i = model.get_value(iterator, 0)
            fineshed = model.get_value(iterator, 1)
            if fineshed == 1:
                db().update('tarefas', i, concluido=0)
            else:
                db().update('tarefas', i, concluido=1)
            self.populate_task_list()

    def menu_popup(self, obj, event):
        """
        menu_popup, shows the menu for the treeview
        """
        # If the mouse button isn't the Right button...pass
        if event.button != 3:
            pass
        else:
            path = obj.get_path_at_pos(int(event.x), int(event.y))
            selection = obj.get_selection()
            selected = selection.get_selected_rows()
            if not path:
                return None
            if path[0] not in selected[1]:
                selection.unselect_all()
                selection.select_path(path[0])
            if selection.count_selected_rows() > 1:
                pass
            else:
                model, iter = selection.get_selected()
                # Get the current status of the task(done or to do);
                done = model.get_value(iter, 1)
                m = gtk.Menu()
                r_task = gtk.MenuItem("Remover Tarefa")
                # If done is equal to one it means that the task is done
                if done == 1:
                    m_done = gtk.MenuItem("Desmarcar como feita")
                else:
                    m_done = gtk.MenuItem("Marcar como feita")

            # Connecting the events.
            m_done.connect('activate', self.finish_task)
            r_task.connect('activate', self.delete_task)
            # Showing all!
            r_task.show()
            m_done.show()
            # Appending the menu itens
            m.append(m_done)
            m.append(r_task)
            # Poping it up.
            m.popup(None, None, None, event.button, event.time, None)
            return False

    def mark_days(self, obj=None):
        """
        Get all days that have tasks within and mark them on the calendar
        """
        calendario = self.w_gui.get_widget('calendario')
        calendario.clear_marks()
        day, month, year = self.get_calendar()
        dias = db().getByDate(None, month)
        for i in dias:
            calendario.mark_day(i[4].day)

    def get_calendar(self):
        cc = self.w_gui.get_widget('calendario')
        year, month, day = cc.get_date()
        month += 1
        day = "%02d" % day

        return day, month, year

    def populate_task_list(self, obj=None):
        """
        Populate the taks list
        and then calls self.mark_days()
        """
        day, month, year = self.get_calendar()
        tasks = db().getListOfTasks(day, month, year)
        # Remove all items on the list
        for i in self.list_tasks:
            self.list_tasks.remove(i.iter)
        # Append new ones.
        for i in tasks:
            if not self.show_done_tasks and i[1] == 1:
                pass
            else:
                self.list_tasks.append(i)
        self.mark_days()

    def start_timer(self, *args):
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
            self.thread_pid = gobject.timeout_add(10, self.run)
        else:
            if self.thread_pid == 0 and model and iter:
                self.alarm(self.alarms['inicio'])
                self.lock_notify = None
                self.idAtivo = model.get_value(iter, 0)
                self.startTime = time.time() + self.time_seconds
                self.thread_pid = gobject.timeout_add(10, self.run)
                self.change_icon('Normal', True)

    def activate(self, obj, event):
        """Stupid ass name, i know, shame on me"""
        if event.button == 3:
            self.stop_timer()
        else:
            if (self.main_window.flags() & gtk.VISIBLE) != 0:
                self.main_window.hide()
            else:
                self.main_window.show()

    def alarm(self, file=None):
        """Play a sound file"""
        if file:
            play().play(file)

    def update_info(self, obj):
        """Get the Info from the list and then update the
        labels, date, pomodoros etc...
        """
        model, iter = obj.get_selection().get_selected()
        if iter:
            id = model.get_value(iter, 0)
            row = db().getByID(id)
            data = datetime.datetime.strftime(row[4], '%d/%m/%Y')
            self.w_gui.get_widget('labelData').set_text(data)
            self.w_gui.get_widget('labelPomodoros').set_text(str(row[3]))
            status = row[1]

            if status == 1:
                self.w_gui.get_widget('labelStatus').set_text('Sim')
            else:
                self.w_gui.get_widget('labelStatus').set_text('Não')

    def stop_timer(self, obj=None):
        """Stop the timer"""
        if self.thread_pid != 0:
            self.lock_notify = False
            if obj:
                self.active_break = False
            self.change_icon('Normal')
            gobject.source_remove(self.thread_pid)
            self.label_clock.set_text("00:00")
            self.startTime = time.time()
            self.thread_pid = 0

    def notificate(self, msg=None):
        """Use pynotify to emit a notification, looks great in ubuntu"""
        if notify and msg:
            if pynotify.init('Pymodoro'):
                n = pynotify.Notification(
                    'Pymodoro', msg, "%s/img/pomodoro.png" % self.filesDir)
                n.show()
                return True
        else:
            return None

    def change_icon(self, icon=None, blinking=None):
        """Use the change the status of the icon, blinking or not, Normal or
        break time"""
        if icon:
            if icon == 'Normal':
                self.staticon.set_from_file("files/img/pomodoro.png")

            elif icon == 'Break':
                self.staticon.set_from_file("./files/img/pomodoro-break.png")
            else:
                return None
            if blinking:
                self.staticon.set_blinking(True)
            else:
                self.staticon.set_blinking(False)

            return True

    def finished(self):
        """Here we define what will happen when the clocks hits 0"""
        self.stop_timer()
        self.lock_notify = False

        if self.active_break:
            if self.pomodoros > 3:
                self.full_break = True
                self.pomodoros = 0
            else:
                self.pomodoros += 1
            self.change_icon('Normal')
            self.alarm(self.alarms['alarm'])
            self.notificate('Descanso Acabou, volta a trabalhar vagabundo!')
            self.active_break = False
        else:
            pomodoros = db().getPomodoros(self.idAtivo) + 1
            self.w_gui.get_widget('labelPomodoros').set_text(str(pomodoros))
            db().update('tarefas', self.idAtivo, pomodoros=pomodoros)
            self.pomodoros = self.pomodoros + 1
            self.change_icon('Break', True)
            self.notificate('Iniciando pausa... 5 minutos, corre negada!.')
            self.alarm(self.alarms['pausacurta'])
            self.active_break = True
            self.start_timer()

    def hide_done_tasks(self, obj=None):
        """Hidden the tasks tagged as done"""
        if not self.show_done_tasks:
            self.show_done_tasks = True
        else:
            self.show_done_tasks = False
        self.populate_task_list()

    def run(self):
        """the function that holds the clock itself"""
        diff_time = self.startTime - time.time()
        (minutes, seconds) = divmod(diff_time, 60.0)
        if int(diff_time) == 0:
            self.finished()
            return False
        else:
            self.label_clock.set_text("%02i:%02i" % (minutes, seconds))

        if int(diff_time) < 120:
            if self.lock_notify:
                pass
            else:
                if self.active_break:
                    self.lock_notify = True
                else:
                    self.notificate('Faltam apenas 2 minutos')
                    self.alarm(self.alarms['2minutes'])
                    self.lock_notify = True
        return True

if __name__ == '__main__':
    app = Pymodoro()
    gtk.gdk.threads_init
    gtk.main()
