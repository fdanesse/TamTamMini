#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Corregido:
#   12/11/2013 Flavio Danesse
#   fdanesse@gmail.com - fdanesse@activitycentral.com

import os
import random
import time
import xdrlib

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from math import sqrt

from common.Util.ThemeWidgets import ImageVScale # Descripcion: Slicer
from common.Util.ThemeWidgets import ImageToggleButton # Descripcion: botón play
from common.Util.ThemeWidgets import ImageButton # Descripcion: botón Dados
from common.Util.ThemeWidgets import ImageRadioButton # Descripcion: botón de instrumento

from common.Util.CSoundNote import CSoundNote
from common.Util import NoteDB
from common.Util.NoteDB import Note
from common.Util.CSoundClient import new_csound_client
from common.Util import InstrumentDB

# Necesario porque crea los instrumentos.
from common.Util.Instruments import DRUMCOUNT
from common.Util import OS
from common.Util.NoteDB import PARAMETER

from common.Config import imagefile

from Fillin import Fillin
from KeyboardStandAlone import KeyboardStandAlone
from MiniSequencer import MiniSequencer
from Loop import Loop
from RythmGenerator import generator

from Mini.InstrumentPanel import InstrumentPanel
#from Mini.miniToolbars import playToolbar
#from Mini.miniToolbars import recordToolbar

from gettext import gettext as _

import common.Util.Network as Net
import common.Config as Config

Tooltips = Config.Tooltips


class miniTamTamMain(Gtk.EventBox):

    def __init__(self, activity):

        Gtk.EventBox.__init__(self)

        self.instrumentPanel = None
        self.activity = activity

        self.instrumentDB = InstrumentDB.getRef()
        self.firstTime = False
        self.playing = False
        self.csnd = new_csound_client()
        self.timeout_ms = 50
        self.instVolume = 50
        self.drumVolume = 0.5
        self.instrument = 'sarangi'
        self.regularity = 0.75
        self.beat = 4
        self.reverb = 0.1
        self.tempo = Config.PLAYER_TEMPO
        self.beatDuration = 60.0 / self.tempo
        self.ticksPerSecond = Config.TICKS_PER_BEAT * self.tempo / 60.0
        self.rythmInstrument = 'drum1kit'
        self.csnd.load_drumkit(self.rythmInstrument)
        self.muteInst = False
        
        self.drumFillin = Fillin(
            self.beat, self.tempo,
            self.rythmInstrument,
            self.reverb, self.drumVolume)

        self.sequencer = MiniSequencer(
            self.recordStateButton,
            self.recordOverSensitivity)
            
        self.loop = Loop(self.beat, sqrt(
            self.instVolume * 0.01))
        self.csnd.setTempo(self.tempo)
        self.noteList = []
        time.sleep(0.001) # why?
        
        for i in range(21):
            self.csnd.setTrackVolume(100, i)

        for i in  range(10):
            r = str(i + 1)
            self.csnd.load_instrument('guidice' + r)

        self.volume = 100
        self.csnd.setMasterVolume(self.volume)
        self.sequencer.beat = self.beat
        self.loop.beat = self.beat

        # Descripcion: Contenedor Principal
        self.mainWindowBox = Gtk.HBox()
        
        self.leftBox = Gtk.VBox()
        self.rightBox = Gtk.VBox()
        
        # Descripcion: Esto está alrevés, self.rightBox está a la izquierda.
        self.mainWindowBox.pack_start(self.rightBox, False, False, 0)
        
        # Descripcion: Esto está alrevés, self.leftBox está a la derecha.
        self.mainWindowBox.pack_start(self.leftBox, True, True, 0)
        
        self.add(self.mainWindowBox)

        self.enableKeyboard()
        self.setInstrument(self.instrument)

        self.connect('key-press-event', self.onKeyPress)
        self.connect('key-release-event', self.onKeyRelease)

        self.drawGeneration()
        self.show_all()
        
        if 'a good idea' == True:
            self.playStartupSound()

        self.beatPickup = True

        self.heartbeatStart = time.time()
        self.syncQueryStart = {}
        self.syncTimeout = None

        self.network = Net.Network()
        self.network.addWatcher(
            self.networkStatusWatcher)
        
        self.network.connectMessage(
            Net.HT_SYNC_REPLY,
            self.processHT_SYNC_REPLY)
            
        self.network.connectMessage(
            Net.HT_TEMPO_UPDATE,
            self.processHT_TEMPO_UPDATE)
            
        self.network.connectMessage(
            Net.PR_SYNC_QUERY,
            self.processPR_SYNC_QUERY)
            
        self.network.connectMessage(
            Net.PR_TEMPO_QUERY,
            self.processPR_TEMPO_QUERY)
            
        self.network.connectMessage(
            Net.PR_REQUEST_TEMPO_CHANGE,
            self.processPR_REQUEST_TEMPO_CHANGE)

        # data packing classes
        self.packer = xdrlib.Packer()
        self.unpacker = xdrlib.Unpacker("")

        #-- handle forced networking ---------------------------------------
        if self.network.isHost():
            self.updateSync()
            self.syncTimeout = GObject.timeout_add(
                1000, self.updateSync)
            
        elif self.network.isPeer():
            self.sendTempoQuery()
            self.syncTimeout = GObject.timeout_add(
                1000, self.updateSync)
        
        #if not Config.HAVE_TOOLBOX:
        #    self.activity.connect("shared", self.shared)

        if os.path.isfile("FORCE_SHARE"):    # HOST
            r = random.random()
            #print "::::: Sharing as TTDBG%f :::::" % r
            #self.activity.set_title(_("TTDBG%f" % r))
            print "::::: Sharing as TamTam :::::"
            self.activity.set_title(_("TamTam"))
            self.activity.share()
            
        elif self.activity.shared_activity: # PEER
            self.activity.shared_activity.connect(
                "buddy-joined", self.buddy_joined)
                
            self.activity.shared_activity.connect(
                "buddy-left", self.buddy_left)
                
            self.activity.connect("joined", self.joined)
            self.network.setMode(Net.MD_WAIT)
            #self.activity.activity_toolbar.share.hide()

    def __make_geneSlider(self):
        """
        slider 1
        """
        
        self.geneSliderBoxImgTop = Gtk.Image()
        self.geneSliderBoxImgTop.set_from_file(
            imagefile('complex6.png'))
            
        self.geneAdjustment = Gtk.Adjustment(
            value=self.regularity, lower=0,
            upper=1, step_incr=0.01,
            page_incr=0, page_size=0)
            
        self.geneSlider = ImageVScale(
            'sliderbutbleu.png',
            self.geneAdjustment, 5)
            
        self.geneSlider.set_inverted(False)
        self.geneAdjustment.connect(
            "value_changed",
            self.handleGenerationSlider)
            
        self.geneSlider.connect(
            "button-release-event",
            self.handleGenerationSliderRelease)
            
        self.geneSlider.set_tooltip_text(Tooltips.COMPL)
        
    def __make_beatSlider(self):
        """
        slider 2
        """

        self.beatSliderBoxImgTop = Gtk.Image()
        self.beatSliderBoxImgTop.set_from_file(
            imagefile('beat3.png'))
        
        self.beatAdjustment = Gtk.Adjustment(
            value=self.beat, lower=2,
            upper=12, step_incr=1,
            page_incr=0, page_size=0)
            
        self.beatSlider = ImageVScale(
            'sliderbutjaune.png',
            self.beatAdjustment, 5, snap=1)
            
        self.beatSlider.set_inverted(True)
        self.beatAdjustment.connect(
            "value_changed",
            self.handleBeatSlider)
            
        self.beatSlider.connect(
            "button-release-event",
            self.handleBeatSliderRelease)
            
        self.beatSlider.set_tooltip_text(Tooltips.BEAT)

    def __make_tempoSlider(self):
        """
        slider 3
        """

        self.delayedTempo = 0 # used to store tempo updates while the slider is active
        self.tempoSliderActive = False

        self.tempoSliderBoxImgTop = Gtk.Image()
        self.tempoSliderBoxImgTop.set_from_file(
            imagefile('tempo5.png'))
            
        self.tempoAdjustment = Gtk.Adjustment(
            value=self.tempo,
            lower=Config.PLAYER_TEMPO_LOWER,
            upper=Config.PLAYER_TEMPO_UPPER,
            step_incr=1, page_incr=1, page_size=1)
            
        self.tempoSlider = ImageVScale(
            'sliderbutvert.png',
            self.tempoAdjustment, 5)
            
        self.tempoSlider.set_inverted(True)
        self.tempoAdjustmentHandler = self.tempoAdjustment.connect(
            "value_changed", self.handleTempoSliderChange)
            
        self.tempoSlider.connect("button-press-event",
            self.handleTempoSliderPress)
            
        self.tempoSlider.connect("button-release-event",
            self.handleTempoSliderRelease)
        
        self.tempoSlider.set_tooltip_text(Tooltips.TEMPO)
        
    def __make_volumeSlider(self):
        """
        slider 4
        """

        self.volumeSliderBoxImgTop = Gtk.Image()
        self.volumeSliderBoxImgTop.set_from_file(
            imagefile('volume2.png'))
            
        self.volumeAdjustment = Gtk.Adjustment(
            value=self.volume, lower=0,
            upper=200, step_incr=1,
            page_incr=1, page_size=1)
            
        self.volumeSlider = ImageVScale(
            'sliderbutbleu.png',
            self.volumeAdjustment, 5)
            
        self.volumeSlider.set_inverted(True)
        self.volumeAdjustment.connect(
            "value_changed", self.handleVolumeSlider)
        
        self.volumeSlider.set_tooltip_text(Tooltips.VOL)
        
    def drawGeneration(self):
        """
        Descripcion:
            Area Izquierda del Panel Principal.
        """
        
        slidersBox = Gtk.VBox()
        slidersBox.set_border_width(Config.PANEL_SPACING)

        geneSliderBox = Gtk.Table(rows=6, columns=4, homogeneous=True)
        
        ### slider 1
        self.__make_geneSlider()
        geneSliderBox.attach(self.geneSliderBoxImgTop, 0, 1, 0, 1)
        geneSliderBox.attach(self.geneSlider, 0, 1, 1, 4)
        
        ### slider 2
        self.__make_beatSlider()
        geneSliderBox.attach(self.beatSliderBoxImgTop, 1, 2, 0, 1)
        geneSliderBox.attach(self.beatSlider, 1, 2, 1, 4)

        ### slider 3
        self.__make_tempoSlider()
        geneSliderBox.attach(self.tempoSliderBoxImgTop, 2, 3, 0, 1)
        geneSliderBox.attach(self.tempoSlider, 2, 3, 1, 4)
        
        ### slider 4
        self.__make_volumeSlider()
        geneSliderBox.attach(self.volumeSliderBoxImgTop, 3, 4, 0, 1)
        geneSliderBox.attach(self.volumeSlider, 3, 4, 1, 4)
        
        ### play button
        self.playButton = ImageToggleButton(
            'miniplay.png', clickImg_path='stop.png')

        self.playButton.connect(
            'clicked', self.handlePlayButton)
            
        geneSliderBox.attach(self.playButton, 0, 2, 4, 6)

        ### dice button
        self.generateBtn = ImageButton('dice.png',
            clickImg_path='diceblur.png')
            
        self.generateBtn.connect(
            'button-press-event',
            self.handleGenerateBtn)
        
        geneSliderBox.attach(self.generateBtn, 2, 4, 4, 6)
        self.generateBtn.set_tooltip_text(Tooltips.GEN)
        
        slidersBox.pack_start(geneSliderBox, False, False, 0)
        self.rightBox.pack_start(slidersBox, False, False, 0)

        ### drum box
        drum_box = Gtk.Table(rows=3, columns=2, homogeneous=True)
        
        drum_scroll = Gtk.ScrolledWindow()
        drum_scroll.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC)
        drum_scroll.add_with_viewport(drum_box)
        
        kit = 1
        drum_group = None
        
        for c in range(0, 2):
            for r in range(0, 3):
                
                drum = ImageRadioButton(
                    group=drum_group,
                    mainImg_path='drum%dkit.png' % kit,
                    width=80)

                drum.connect('clicked',
                    self.handleGenerationDrumBtn,
                    'drum%dkit' % kit)
                    
                drum_box.attach(drum, c, c+1, r, r+1)

                drum_name = 'drum%dkit' % kit
                hint = self.instrumentDB.instNamed[drum_name].nameTooltip
                drum.set_tooltip_text(hint)

                if not drum_group:
                    drum_group = drum
                    
                kit += 1

        self.rightBox.pack_start(drum_scroll, True, True, 0)

    def loopSettingsChannel(self, channel, value):
        self.csnd.setChannel(channel, value)

    def loopSettingsPlayStop(self, state, loop):
    
        if not state:
            if loop:
                self.loopSettingsPlaying = True
                self.csnd.inputMessage(Config.CSOUND_PLAY_LS_NOTE % 5022)
                
            else:
                self.csnd.inputMessage(Config.CSOUND_PLAY_LS_NOTE % 5023)
                
        else:
            if loop:
                self.loopSettingsPlaying = False
                self.csnd.inputMessage(Config.CSOUND_STOP_LS_NOTE)

    def load_ls_instrument(self, soundName):
        self.csnd.load_ls_instrument(soundName)

    def updateInstrumentPanel(self):
        
        if self.instrumentPanel is None:
            self.instrumentPanel = InstrumentPanel() # Descripcion: Area Derecha.
            self.leftBox.pack_start(self.instrumentPanel, True, True, 0)

        screen = Gdk.Screen.get_default()
        width = screen.get_width() - self.rightBox.get_size_request()[0]
        
        self.instrumentPanel.configure(
            self.setInstrument,
            self.playInstrumentNote,
            False, self.micRec, width=width)

        self.instrumentPanel.load()

    def micRec(self, widget, mic):
    
        self.csnd.inputMessage("i5600 0 4")
        OS.arecord(4, "crop.csd", mic)
        self.micTimeout = GObject.timeout_add(200,
            self.loadMicInstrument, mic)
            
        self.instrumentPanel.set_activeInstrument(mic, True)
        self.setInstrument(mic)

    def recordStateButton(self, button, state):
    
        if button == 1:
            #self._recordToolbar.keyboardRecButton.set_active(state)
            pass
            
        else:
            #self._recordToolbar.keyboardRecOverButton.set_active(state)
            pass

    def recordOverSensitivity(self, state):
        pass

    def loadMicInstrument(self, data):
        self.csnd.load_mic_instrument(data)

    def regenerate(self):
    
        def flatten(ll):
            rval = []
            
            for l in ll:
                rval += l
                
            return rval
            
        if self.beatPickup:
            self.pickupNewBeat()
            
        noteOnsets = []
        notePitchs = []
        i = 0
        self.noteList= []
        self.csnd.loopClear()
        
        for x in flatten(
            generator(self.rythmInstrument,
            self.beat, 0.8, self.regularity, self.reverb)):
                
            x.amplitude = x.amplitude * self.drumVolume
            noteOnsets.append(x.onset)
            notePitchs.append(x.pitch)
            n = Note(0, x.trackId, i, x)
            self.noteList.append((x.onset, n))
            i = i + 1
            self.csnd.loopPlay(n, 1) #add as active
            
        self.csnd.loopSetNumTicks(self.beat * Config.TICKS_PER_BEAT)
        self.drumFillin.unavailable(noteOnsets, notePitchs)
        self.recordOverSensitivity(False)
        
        if self.playing:
            self.csnd.loopStart()

    def adjustDrumVolume(self):
        for n in self.noteList:
            self.csnd.loopUpdate(n[1],
                PARAMETER.AMPLITUDE,
                n[1].cs.amplitude * self.drumVolume, 1)

    def handleClose(self, widget):
    
        if self.playStopButton.get_active() == True:
            self.playStopButton.set_active(False)
            
        self.sequencer.clearSequencer()
        self.csnd.loopClear()
        self.activity.close()

    def handleGenerationSlider(self, adj):
    
        img = int(adj.get_value() * 7)+1
        self.geneSliderBoxImgTop.set_from_file(
            imagefile('complex' + str(img) + '.png'))

    def handleGenerationSliderRelease(self, widget, event):
    
        self.regularity = widget.get_adjustment().value
        self.beatPickup = False
        self.regenerate()
        self.beatPickup = True

    def pickupNewBeat(self):
    
        self.beat = random.randint(2, 12)
        img = self.scale(self.beat, 2, 12, 1, 11)
        self.beatSliderBoxImgTop.set_from_file(
            imagefile('beat' + str(img) + '.png'))
        self.beatAdjustment.set_value(self.beat)

        self.regularity = random.randint(50, 100) * 0.01
        img = int(self.regularity * 7)+1
        self.geneSliderBoxImgTop.set_from_file(
            imagefile('complex' + str(img) + '.png'))
        self.geneAdjustment.set_value(self.regularity)

        self.sequencer.beat = self.beat
        self.loop.beat = self.beat
        self.drumFillin.setBeats(self.beat)

    def handleBeatSlider(self, adj):
    
        img = self.scale(int(adj.get_value()), 2, 12, 1, 11)
        self.beatSliderBoxImgTop.set_from_file(
            imagefile('beat' + str(img) + '.png'))
        self.sequencer.beat = self.beat
        self.loop.beat = self.beat
        self.drumFillin.setBeats(self.beat)

    def handleBeatSliderRelease(self, widget, event):
    
        self.beat = int(widget.get_adjustment().value)
        self.sequencer.beat = self.beat
        self.loop.beat = self.beat
        self.drumFillin.setBeats(self.beat)
        self.beatPickup = False
        self.regenerate()
        self.beatPickup = True

    def handleTempoSliderPress(self, widget, event):
        self.tempoSliderActive = True

    def handleTempoSliderRelease(self, widget, event):
    
        self.tempoSliderActive = False
        if self.network.isPeer() and self.delayedTempo != 0:
            if self.tempo != self.delayedTempo:
                self.tempoAdjustment.handler_block(self.tempoAdjustmentHandler)
                self.tempoAdjustment.set_value(self.delayedTempo)
                self._updateTempo(self.delayedTempo)
                self.tempoAdjustment.handler_unblock(self.tempoAdjustmentHandler)
                
            self.delayedTempo = 0
            self.sendSyncQuery()

    def handleTempoSliderChange(self, adj):
    
        if self.network.isPeer():
            self.requestTempoChange(int(adj.get_value()))
            
        else:
            self._updateTempo(int(adj.get_value()))

    def _updateTempo(self, val):

        if self.network.isHost():
            t = time.time()
            percent = self.heartbeatElapsed() / self.beatDuration

        self.tempo = val
        self.beatDuration = 60.0/self.tempo
        self.ticksPerSecond = Config.TICKS_PER_BEAT * self.tempo/60.0
        self.csnd.setTempo(self.tempo)
        self.sequencer.tempo = self.tempo
        self.drumFillin.setTempo(self.tempo)

        if self.network.isHost():
            self.heatbeatStart = t - percent * self.beatDuration
            self.updateSync()
            self.sendTempoUpdate()

        img = int(self.scale(self.tempo,
            Config.PLAYER_TEMPO_LOWER,
            Config.PLAYER_TEMPO_UPPER,
            1, 9))
            
        self.tempoSliderBoxImgTop.set_from_file(
            imagefile('tempo' + str(img) + '.png'))

    def handleBalanceSlider(self, adj):
        
        self.instVolume = int(adj.get_value())
        self.drumVolume = sqrt((100-self.instVolume) * 0.01)
        self.adjustDrumVolume()
        self.drumFillin.setVolume(self.drumVolume)
        instrumentVolume = sqrt(self.instVolume * 0.01)
        self.loop.adjustLoopVolume(instrumentVolume)
        self.sequencer.adjustSequencerVolume(instrumentVolume)
        img = int(self.scale(self.instVolume, 100, 0, 0, 4.9))
        
        #self._playToolbar.balanceSliderImgLeft.set_from_file(
        #    imagefile('dru' + str(img) + '.png'))
            
        img2 = int(self.scale(self.instVolume, 0, 100, 0, 4.9))
        
        #self._playToolbar.balanceSliderImgRight.set_from_file(
        #    imagefile('instr' + str(img2) + '.png'))

    def handleReverbSlider(self, adj):
    
        self.reverb = adj.get_value()
        self.drumFillin.setReverb(self.reverb)
        img = int(self.scale(self.reverb, 0, 1, 0, 4))
        
        #self._playToolbar.reverbSliderImgRight.set_from_file(
        #    imagefile('reverb' + str(img) + '.png'))
            
        self.keyboardStandAlone.setReverb(self.reverb)

    def handleVolumeSlider(self, adj):
    
        self.volume = adj.get_value()
        self.csnd.setMasterVolume(self.volume)
        img = int(self.scale(self.volume, 0, 200, 0, 3.9))
        self.volumeSliderBoxImgTop.set_from_file(
            imagefile('volume' + str(img) + '.png'))

    def handlePlayButton(self, widget, data=None):
        # use widget.get_active() == False when calling this on 'clicked'
        # use widget.get_active() == True when calling this on button-press-event
        if widget.get_active() == False:
            self.drumFillin.stop()
            self.sequencer.stopPlayback()
            self.csnd.loopPause()
            self.playing = False
            
        else:
            if not self.firstTime:
                self.regenerate()
                self.firstTime = True
                
            self.drumFillin.play()
            #self.csnd.loopSetTick(0)
            nextInTicks = self.nextHeartbeatInTicks()
            self.csnd.loopSetTick(
                Config.TICKS_PER_BEAT * self.beat - int(round(nextInTicks)))
            self.csnd.loopStart()
            self.playing = True

    def handleGenerationDrumBtn(self, widget, data):
    
        #data is drum1kit, drum2kit, or drum3kit
        #print 'HANDLE: Generate Button'
        self.rythmInstrument = data
        self.csnd.load_drumkit(data)
        instrumentId = self.instrumentDB.instNamed[data].instrumentId
        
        for (o, n) in self.noteList:
            self.csnd.loopUpdate(n, NoteDB.PARAMETER.INSTRUMENT, instrumentId, -1)
            
        self.drumFillin.setInstrument(self.rythmInstrument)

    def handleGenerateBtn(self, widget, data=None):
    
        self.regenerate()
        if not self.playButton.get_active():
            self.playButton.set_active(True)

        #this calls sends a 'clicked' event,
        #which might be connected to handlePlayButton
        self.playStartupSound()

    def enableKeyboard(self):
        
        self.keyboardStandAlone = KeyboardStandAlone(
            self.sequencer.recording,
            self.sequencer.adjustDuration,
            self.csnd.loopGetTick,
            self.sequencer.getPlayState, self.loop)
            
        #self.add_events(Gdk.EvenMask.BUTTON_PRESS_MASK)

    def setInstrument(self, instrument):
    
        self.instrument = instrument
        self.keyboardStandAlone.setInstrument(instrument)
        self.csnd.load_instrument(instrument)

    def playInstrumentNote(self, instrument, secs_per_tick = 0.025):
    
        if not self.muteInst:
            self.csnd.play(
                CSoundNote(
                    onset = 0,
                    pitch = 36,
                    amplitude = 1,
                    pan = 0.5,
                    duration = 20,
                    trackId = 1,
                    instrumentId = self.instrumentDB.instNamed[
                        instrument].instrumentId,
                    reverbSend = self.reverb,
                    tied = False,
                    mode = 'mini'),
                    secs_per_tick)

    def onKeyPress(self, widget, event):
        
        if event.hardware_keycode == 219: #'/*' button to reset drum loop
            if self.playStopButton.get_active() == True:
                self.handlePlayButton(self.playStopButton)
                self.playStopButton.set_active(False)
                self.handlePlayButton(self.playStopButton)
                self.playStopButton.set_active(True)

        if event.hardware_keycode == 37:
            if self.muteInst:
                self.muteInst = False
                
            else:
                self.muteInst = True

        if event.hardware_keycode == 65: #what key is this? what feature is this?
            pass
            #if self.playStopButton.get_active():
                #self.playStopButton.set_active(False)
            #else:
                #self.playStopButton.set_active(True)

        self.keyboardStandAlone.onKeyPress(widget, event, sqrt(self.instVolume*0.01))

    def onKeyRelease(self, widget, event):
        self.keyboardStandAlone.onKeyRelease(widget, event)

    def playStartupSound(self):
        r = str(random.randrange(1, 11))
        self.playInstrumentNote('guidice' + r)

    def onActivate(self, arg):
        self.csnd.loopPause()
        self.csnd.loopClear()

    # FIXME: SubActivity no está definido.
    #def onDeactivate( self ):
    #    SubActivity.onDeactivate( self )
    #    self.csnd.loopPause()
    #    self.csnd.loopClear()

    def onDestroy(self):
        self.network.shutdown()

    def scale(self, input, input_min, input_max, output_min, output_max):
        
        range_input = input_max - input_min
        range_output = output_max - output_min
        result = (input - input_min) * range_output / range_input + output_min

        if (input_min > input_max and output_min > output_max) or \
            (output_min > output_max and input_min < input_max):
            
            if result > output_min:
                return output_min
                
            elif result < output_max:
                return output_max
                
            else:
                return result

        if (input_min < input_max and output_min < output_max) or \
            (output_min < output_max and input_min > input_max):
                
            if result > output_max:
                return output_max
                
            elif result < output_min:
                return output_min
                
            else:
                return result

    #-----------------------------------------------------------------------
    # Network

    #-- Activity -----------------------------------------------------------
    def shared(self, activity):
        
        if Config.DEBUG:
            print "miniTamTam:: successfully shared, start host mode"
            
        self.activity._shared_activity.connect(
            "buddy-joined", self.buddy_joined)
            
        self.activity._shared_activity.connect(
            "buddy-left", self.buddy_left)
            
        self.network.setMode(Net.MD_HOST)
        self.updateSync()
        self.syncTimeout = GObject.timeout_add(
            1000, self.updateSync)

    def joined(self, activity):
    
        print "miniTamTam:: joined activity!!"
        
        for buddy in self.activity._shared_activity.get_joined_buddies():
            print buddy.props.ip4_address

    def buddy_joined(self, activity, buddy):
    
        print "buddy joined " + str(buddy)
        try:
            print buddy.props.ip4_address
            
        except:
            print "bad ip4_address"
            
        if self.network.isHost():
            # TODO how do I figure out if this buddy is me?
            if buddy.props.ip4_address:
                self.network.introducePeer(buddy.props.ip4_address)
                
            else:
                print "miniTamTam:: new buddy does not have an ip4_address!!"

    def buddy_left(self, activity, buddy):
        print "buddy left"

    #def joined( self, activity ):
    #    if Config.DEBUG: print "miniTamTam:: successfully joined, wait for host"
    #    self.net.waitForHost()

    #-- Senders ------------------------------------------------------------

    def sendSyncQuery(self):
    
        self.packer.pack_float(random.random())
        hash = self.packer.get_buffer()
        self.packer.reset()
        self.syncQueryStart[hash] = time.time()
        self.network.send(Net.PR_SYNC_QUERY, hash)

    def sendTempoUpdate(self):
    
        self.packer.pack_int(self.tempo)
        self.network.sendAll(Net.HT_TEMPO_UPDATE,
            self.packer.get_buffer())
        self.packer.reset()

    def sendTempoQuery(self):
        self.network.send(Net.PR_TEMPO_QUERY)

    def requestTempoChange(self, val):
        self.packer.pack_int(val)
        self.network.send(Net.PR_REQUEST_TEMPO_CHANGE,
            self.packer.get_buffer())
        self.packer.reset()

    #-- Handlers -----------------------------------------------------------

    def networkStatusWatcher(self, mode):
    
        if mode == Net.MD_OFFLINE:
            if self.syncTimeout:
                GObject.source_remove(self.syncTimeout)
                self.syncTimeout = None
                
        if mode == Net.MD_PEER:
            self.updateSync()
            
            if not self.syncTimeout:
                self.syncTimeout = GObject.timeout_add(
                    1000, self.updateSync)
                
            self.sendTempoQuery()

    def processHT_SYNC_REPLY(self, sock, message, data):
    
        t = time.time()
        hash = data[0:4]
        latency = t - self.syncQueryStart[hash]
        self.unpacker.reset(data[4:8])
        nextBeat = self.unpacker.unpack_float()
        #print "mini:: got sync: next beat in %f, latency %d" % (nextBeat, latency*1000)
        self.heartbeatStart = t + nextBeat - self.beatDuration - latency/2
        self.correctSync()
        self.syncQueryStart.pop(hash)

    def processHT_TEMPO_UPDATE(self, sock, message, data):
    
        self.unpacker.reset(data)
        val = self.unpacker.unpack_int()
        
        if self.tempoSliderActive:
            self.delayedTempo = val
            return
            
        self.tempoAdjustment.handler_block(
            self.tempoAdjustmentHandler)
            
        self.tempoAdjustment.set_value(val)
        self._updateTempo(val)
        self.tempoAdjustment.handler_unblock(
            self.tempoAdjustmentHandler)
            
        self.sendSyncQuery()

    def processPR_SYNC_QUERY(self, sock, message, data):
        self.packer.pack_float(self.nextHeartbeat())
        self.network.send(Net.HT_SYNC_REPLY, data + self.packer.get_buffer(), sock)
        self.packer.reset()

    def processPR_TEMPO_QUERY(self, sock, message, data):
        self.packer.pack_int(self.tempo)
        self.network.send(Net.HT_TEMPO_UPDATE, self.packer.get_buffer(), to = sock)
        self.packer.reset()

    def processPR_REQUEST_TEMPO_CHANGE(self, sock, message, data):
        
        if self.tempoSliderActive:
            return
            
        self.unpacker.reset(data)
        val = self.unpacker.unpack_int()
        self.tempoAdjustment.set_value(val)

    #-----------------------------------------------------------------------
    # Sync
    def nextHeartbeat(self):
        delta = time.time() - self.heartbeatStart
        return self.beatDuration - (delta % self.beatDuration)

    def nextHeartbeatInTicks(self):
        delta = time.time() - self.heartbeatStart
        next = self.beatDuration - (delta % self.beatDuration)
        return self.ticksPerSecond*next

    def heartbeatElapsed(self):
        delta = time.time() - self.heartbeatStart
        return delta % self.beatDuration

    def heartbeatElapsedTicks(self):
        delta = time.time() - self.heartbeatStart
        return self.ticksPerSecond*(delta % self.beatDuration)

    def updateSync(self):
    
        if self.network.isOffline():
            return False
            
        elif self.network.isWaiting():
            return True
            
        elif self.network.isHost():
            self.correctSync()
            
        else:
            self.sendSyncQuery()
            
        return True

    def correctSync(self):
    
        curTick = self.csnd.loopGetTick()
        curTicksIn = curTick % Config.TICKS_PER_BEAT
        ticksIn = self.heartbeatElapsedTicks()
        err = curTicksIn - ticksIn
        
        if err > Config.TICKS_PER_BEAT_DIV2:
            err -= Config.TICKS_PER_BEAT
            
        elif err < -Config.TICKS_PER_BEAT_DIV2:
            err += Config.TICKS_PER_BEAT
            
        correct = curTick - err
        ticksPerLoop = Config.TICKS_PER_BEAT * self.beat
        
        if correct > ticksPerLoop:
            correct -= ticksPerLoop
            
        elif correct < 0:
            correct += ticksPerLoop
            
        if abs(err) > 0.25:
            self.csnd.adjustTick(-err)

# FIXME: miniTamTam no está definido
#if __name__ == "__main__":
#    MiniTamTam = miniTamTam()
#    #start the gtk event loop
#    gtk.main()
