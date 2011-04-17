#!/usr/bin/env python2.6

import time, pygtk, os, pango, gobject

pygtk.require('2.0')

import gtk
from gtk import glade




class main:
    
    def __init__(self):
        
        self.rolling = 0
        
        self.filesDir = os.path.abspath('files')
        self.wGui = glade.XML("%s/gui/main.glade" % self.filesDir)
        self.mainWindow = self.wGui.get_widget('janelaPrincipal')
        self.labelClock = self.wGui.get_widget('labelClock')
        self.labelClock.modify_font(pango.FontDescription("22"))
        self.labelClock.set_padding(10, 5)
        self.mainWindow.show_all()
        signals = {
            'on_janelaPrincipal_destroy' : gtk.main_quit,
            'on_startBotao_clicked' : self.startTimer,
            'on_stopBotao_clicked' : self.stopTimer
            
        }
        self.wGui.signal_autoconnect(signals)
        
    def startTimer(self, *args):
        
        if self.rolling == 0:
            self.startTime = time.time()
            self.rolling = gobject.timeout_add(10,self.contar)
        
    def stopTimer(self, *args):
        
        if self.rolling != 0:
            
            gobject.source_remove(self.rolling)
            self.labelClock.set_text("00:00")
            
    def contar(self):   
        
        diferenca = time.time() - self.startTime
        (minutoss, segundos) = divmod(diferenca, 60.0)
        
        self.labelClock.set_text("%02i:%02i" % (minutoss,segundos))
        
        return True
        
app = main()
gtk.main()