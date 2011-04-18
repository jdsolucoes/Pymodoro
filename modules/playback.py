#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

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
    

    
