#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Corregido:
#   12/11/2013 Flavio Danesse
#   fdanesse@gmail.com - fdanesse@activitycentral.com

import random
import common.Config as Config

from common.Generation.GenerationConstants import GenerationConstants
#from common.Generation.Utils import *
from common.Util import InstrumentDB

class GenRythm():
    
    def drumRythmSequence(self, instrumentName, nbeats, density, regularity):
        
        instrumentDB = InstrumentDB.getRef()
        rythmSequence = []
        binSelection = []
        downBeats = []
        upBeats = []
        countDown = 0
        onsetTime = None

        if instrumentDB.instNamed[instrumentName].instrumentRegister == Config.PUNCH:
            registerDensity = 0.5
            downBeatRecurence = 4
            downBeats = [x for x in GenerationConstants.DRUM_PUNCH_ACCENTS[nbeats]]
            
            for downBeat in downBeats:
                upBeats.append(downBeat + Config.TICKS_PER_BEAT / 2)

        if instrumentDB.instNamed[instrumentName].instrumentRegister == Config.LOW:
            registerDensity =1
            downBeatRecurence = 4
            downBeats = [x for x in GenerationConstants.DRUM_LOW_ACCENTS[nbeats]]
            
            for downBeat in downBeats:
                upBeats.append(downBeat + Config.TICKS_PER_BEAT / 2)

        if instrumentDB.instNamed[instrumentName].instrumentRegister == Config.MID:
            registerDensity = .75
            downBeatRecurence = 1
            downBeats = [x for x in GenerationConstants.DRUM_MID_ACCENTS[nbeats]]
            
            for downBeat in downBeats:
                upBeats.append(downBeat + Config.TICKS_PER_BEAT / 4)

        if instrumentDB.instNamed[instrumentName].instrumentRegister == Config.HIGH:
            registerDensity = 1.5
            downBeatRecurence = 1
            downBeats = [x for x in GenerationConstants.DRUM_HIGH_ACCENTS[nbeats]]
            
            for downBeat in downBeats:
                upBeats.append(downBeat + Config.TICKS_PER_BEAT / 4)

        realDensity = density * registerDensity
        
        if realDensity > 1.:
            realDensity = 1.

        list = range(int(realDensity * len(downBeats)))
        
        for i in list:
            if random.random() < (regularity * downBeatRecurence) and \
            binSelection.count(1) < len(downBeats):
                binSelection.append(1)
                
            else:
                if binSelection.count(0) < len(downBeats):
                    binSelection.append(0)
                    
                else:
                    binSelection.append(1)

        countDown = binSelection.count(1)

        length = len(downBeats) - 1
        
        for i in range(countDown):
            ran1 = random.randint(0, length)
            ran2 = random.randint(0, length)
            randMin = min(ran1, ran2)
            onsetTime = downBeats.pop(randMin)
            rythmSequence.append(onsetTime)
            length -= 1

        length = len(upBeats) - 1
        for i in range(len(binSelection) - countDown):
            ran1 = random.randint(0, length)
            ran2 = random.randint(0, length)
            randMin = min(ran1, ran2)
            onsetTime = upBeats.pop(randMin)
            rythmSequence.append(onsetTime)
            length -= 1

        rythmSequence.sort()
        return rythmSequence
