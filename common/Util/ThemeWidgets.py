#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Corregido:
#   12/11/2013 Flavio Danesse
#   fdanesse@gmail.com - fdanesse@activitycentral.com

import gtk

from common.Config import imagefile

from sugar.graphics.combobox import ComboBox
from sugar.graphics.palette import WidgetInvoker

class ITYPE:
    PIXBUF = 0
    PIXMAP = 1


class ImageVScale(gtk.VScale):
    
    def __init__(self, image_name,
        adjustment=None, slider_border=0,
        insensitive_name=None, trough_color="#3D403A",
        snap=False):

        image_name = imagefile(image_name)

        gtk.VScale.__init__(self, adjustment)

        if snap:
            self.snap = 1 / snap
            
        else:
            self.snap = False

        colormap = self.get_colormap()
        self.troughcolor = colormap.alloc_color(
            trough_color, True, True)

        img = gtk.Image()
        img.set_from_file(image_name)
        self.sliderPixbuf = img.get_pixbuf()

        if insensitive_name == None:
            self.insensitivePixbuf = None
            
        else:
            img = gtk.Image()
            img.set_from_file(insensitive_name)
            self.insensitivePixbuf = img.get_pixbuf()

        name = image_name + "ImageVScale"
        self.set_name(name)

        rc_str = """
style "scale_style" {
    GtkRange::slider_width = %d
    GtkScale::slider_length = %d
}
widget "*%s*" style "scale_style"
        """ % (self.sliderPixbuf.get_width(),
        self.sliderPixbuf.get_height(), name)
        gtk.rc_parse_string(rc_str)

        self.pixbufWidth = self.sliderPixbuf.get_width()
        self.pixbufHeight = self.sliderPixbuf.get_height()
        self.sliderBorder = slider_border
        self.sliderBorderMUL2 = self.sliderBorder*2

        self.set_draw_value(False)

        self.connect("expose-event", self.expose)
        self.connect("size-allocate", self.size_allocate)
        self.connect("button-release-event", self.button_release)
        adjustment.connect("value-changed", self.value_changed)

    def size_allocate(self, widget, allocation):
    
        self.alloc = allocation
        self.sliderX = self.alloc.width / 2 - self.pixbufWidth / 2
        return False

    def set_snap(self, snap):
    
        if snap:
            self.snap = 1 / snap
            
        else:
            self.snap = False
            
        self.queue_draw()

    def value_changed(self, adjustment):
    
        if self.snap:
            val = round(self.snap * self.get_value()) / self.snap
            
            if val != self.get_value():
                self.set_value(val)

    def expose(self, widget, event):

        style = self.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]

        gc.foreground = self.troughcolor

        self.window.draw_rectangle(
            gc, True, self.alloc.x + self.alloc.width / 2 - 1,
            self.alloc.y + self.sliderBorder, 3,
            self.alloc.height - self.sliderBorderMUL2)

        val = self.get_value()
        
        if self.snap:
            val = round(self.snap * val) / self.snap
            
        adj = self.get_adjustment()
        
        if self.get_inverted():
            sliderY = int((
                self.alloc.height - self.pixbufHeight) * (
                adj.upper-val) / (adj.upper - adj.lower))
                
        else:
            sliderY = int((
                self.alloc.height - self.pixbufHeight) * (
                val-adj.lower) / (adj.upper - adj.lower))

        if self.insensitivePixbuf != None and \
            self.state == gtk.STATE_INSENSITIVE:
            self.window.draw_pixbuf(
                gc, self.insensitivePixbuf, 0, 0,
                self.alloc.x + self.sliderX,
                self.alloc.y + sliderY, self.pixbufWidth,
                self.pixbufHeight, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)
                
        else:
            self.window.draw_pixbuf(
                gc, self.sliderPixbuf, 0, 0,
                self.alloc.x + self.sliderX,
                self.alloc.y + sliderY,
                self.pixbufWidth, self.pixbufHeight,
                gtk.gdk.RGB_DITHER_NORMAL, 0, 0 )

        return True

    def button_release(self, widget, event):

        if self.snap:
            self.set_value(round(
                self.snap * self.get_value()) / self.snap)

class ImageButton(gtk.Button):
    
    def __init__(self, mainImg_path,
        clickImg_path=None):
            
        gtk.Button.__init__(self)
        
        mainImg_path = imagefile(mainImg_path)
        clickImg_path = imagefile(clickImg_path)
        
        self.image = gtk.Image()
        hbox = gtk.HBox()
        hbox.pack_start(self.image, True, True, 0)
        
        self.mainImg = gtk.gdk.pixbuf_new_from_file(mainImg_path)
        self.clickImg_path = gtk.gdk.pixbuf_new_from_file(clickImg_path)
        
        self.image.set_from_pixbuf(self.mainImg)
        
        self.add(hbox)
        
        self.show_all()
        
        self.connect('pressed', self.on_btn_press)
        self.connect('released', self.on_btn_release)
            
    def on_btn_release(self, widget):
        self.image.set_from_pixbuf(self.mainImg)

    def on_btn_press(self, widget):
        self.image.set_from_pixbuf(self.clickImg_path)


class ImageToggleButton(gtk.ToggleButton):

    def __init__(self, mainImg_path,
        clickImg_path=None):

        gtk.ToggleButton.__init__(self)
        
        mainImg_path = imagefile(mainImg_path)
        clickImg_path = imagefile(clickImg_path)
        
        self.image = gtk.Image()
        hbox = gtk.HBox()
        hbox.pack_start(self.image, True, True, 0)
        
        self.mainImg = gtk.gdk.pixbuf_new_from_file(mainImg_path)
        self.clickImg_path = gtk.gdk.pixbuf_new_from_file(clickImg_path)
        
        self.image.set_from_pixbuf(self.mainImg)
        
        self.add(hbox)
        
        self.show_all()
        
        self.connect('toggled', self.toggleImage)
        
    def toggleImage(self, widget):
    
        if not self.get_active():
            self.image.set_from_pixbuf(self.mainImg)
            
        else:
            self.image.set_from_pixbuf(self.clickImg_path)


class ImageRadioButton(gtk.RadioButton):

    def __init__(self, group, mainImg_path=None, width=100):
        
        gtk.RadioButton.__init__(self, group)
        
        mainImg_path = imagefile(mainImg_path)
        
        self.image = gtk.Image()
        
        mainImg = gtk.gdk.pixbuf_new_from_file_at_size(
            mainImg_path, width, width)
        
        self.image.set_from_pixbuf(mainImg)
        self.set_image(self.image)
        
        self.set_property('draw-indicator', False)
        self.show_all()


class BigComboBox(ComboBox):

    def __init__(self):
    
        ComboBox.__init__(self)
    
    def append_item(self, action_id, text,
        icon_name=None, size=None, pixbuf=None):

        if not self._icon_renderer and (icon_name or pixbuf):
            self._icon_renderer = gtk.CellRendererPixbuf()

            settings = self.get_settings()
            
            w, h = gtk.icon_size_lookup_for_settings(
                settings, gtk.ICON_SIZE_MENU)
                
            self._icon_renderer.props.stock_size = w

            self.pack_start(self._icon_renderer, False)
            self.add_attribute(self._icon_renderer, 'pixbuf', 2)

        if not self._text_renderer and text:
            self._text_renderer = gtk.CellRendererText()
            self.pack_end(self._text_renderer, True)
            self.add_attribute(self._text_renderer, 'text', 1)

        if not pixbuf:
            if icon_name:
                if not size:
                    size = gtk.ICON_SIZE_LARGE_TOOLBAR
                    width, height = gtk.icon_size_lookup(size)
                    
                else:
                    width, height = size
                    
                if icon_name[0:6] == "theme:": 
                    icon_name = self._get_real_name_from_theme(
                        icon_name[6:], size)
                    
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                    icon_name, width, height)
                    
            else:
                pixbuf = None

        self._model.append([action_id, text, pixbuf, False])
