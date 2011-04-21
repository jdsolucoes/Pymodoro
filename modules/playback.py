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
import alsaaudio
from th import Async


@Async
def play (file=None):
    card = 'default'
    f = open(file,'rb')
    saida = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,card=card)
    saida.setchannels(1)
    saida.setrate(44100)
    saida.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    saida.setperiodsize(160)
    data = f.read()
    saida.write(data)
    return None
    

    
