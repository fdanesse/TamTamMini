#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (c) 2007-8 Jean Piche, Olivier Belanger, James Bergstra
#Copyright (c) 2007-8 Nathanael Lecaude, Adrian Martin, Eric Lamothe
#Copyright (c) 2009-11 Aleksey Lim, Chris Leonard, Douglas Eck
#Copyright (c) 2009-11 Gonzalo Odiard, James Cameron, Jorge Saldivar
#Copyright (c) 2009-11 Marco Pesenti Gritti, Rafael Ortiz, Sean Wood
#Copyright (c) 2011 Walter Bender

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Corregido:
#   12/11/2013 Flavio Danesse
#   fdanesse@gmail.com - fdanesse@activitycentral.com

import locale
locale.setlocale(locale.LC_NUMERIC, 'C')
import os
from gi.repository import Gtk

from common.Util.CSoundClient import new_csound_client

#from Mini.miniTamTamMain import miniTamTamMain

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton


class TamTamMini(activity.Activity):

    __gtype_name__ = 'TamTamMiniWindow'

    def __init__(self, handle):

        self.mini = None

        activity.Activity.__init__(self, handle)

        self.set_title('TamTam Mini')

        #self.connect('notify::active', self.onActive)
        #self.connect('destroy', self.onDestroy)

        toolbox = ToolbarBox()
        separador = Gtk.SeparatorToolItem()
        separador.props.draw = False
        separador.set_expand(True)
        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>q'

        toolbox.toolbar.insert(ActivityToolbarButton(self), -1)
        toolbox.toolbar.insert(separador, -1)
        toolbox.toolbar.insert(stop_button, -1)

        self.set_toolbar_box(toolbox)
  
        #self.mini = miniTamTamMain(self)
        #self.mini.onActivate(arg=None)
        #self.mini.updateInstrumentPanel()

        #self.set_canvas(self.mini)

        self.show_all()

    def do_size_allocate(self, allocation):

        activity.Activity.do_size_allocate(self, allocation)

        if self.mini is not None:
            self.mini.updateInstrumentPanel()

    def onActive(self, widget=None, event=None):

        if widget.props.active == False:
            csnd = new_csound_client()
            csnd.connect(False)

        else:
            csnd = new_csound_client()
            csnd.connect(True)

    def onDestroy(self, arg2):
        '''
        self.mini.onDestroy()
        '''
        csnd = new_csound_client()
        csnd.connect(False)
        csnd.destroy()

        Gtk.main_quit()

    # no more dir created by TamTam
    def ensure_dir(self, dir, perms=0777, rw=os.R_OK | os.W_OK):

        if not os.path.isdir(dir):
            try:
                os.makedirs(dir, perms)

            except OSError, e:
                print 'ERROR:Failed to make dir %s: %i (%s)\n' % (
                    dir, e.errno, e.strerror)

        if not os.access(dir, rw):
            print 'ERROR: directory %s is missing required r/w access\n' % dir

    def read_file(self, file_path):
        self.metadata['tamtam_subactivity'] = 'mini'

    def write_file(self, file_path):
        f = open(file_path, 'w')
        f.close()
