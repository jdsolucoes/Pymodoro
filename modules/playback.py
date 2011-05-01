#!/usr/bin/env python
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
import commands

import threading
import gtk

class play(threading.Thread):
    
    def play(self,file=None):
        if file:
            self.file = file
        self.start()
        
    def run (self):
        
        d = commands.getoutput('mplayer -quiet %s' % self.file)
        
    

    
