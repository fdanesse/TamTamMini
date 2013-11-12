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

        gtk.VScale.__init__( self, adjustment )

        if snap:
            self.snap = 1 / snap
            
        else:
            self.snap = False

        colormap = self.get_colormap()
        self.troughcolor = colormap.alloc_color(
            trough_color, True, True )

        img = gtk.Image()
        img.set_from_file(image_name)
        self.sliderPixbuf = img.get_pixbuf()

        if insensitive_name == None:
            self.insensitivePixbuf = None
            
        else:
            img = gtk.Image()
            img.set_from_file( insensitive_name )
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


class RoundHBox(gtk.HBox):
    
    def __init__( self, radius = 5,
        fillcolor = "#000", bordercolor = "#FFF",
        homogeneous = False, spacing = 0):
            
        gtk.HBox.__init__( self, homogeneous, spacing )
        
        self.alloc = None

        self.radius = radius

        colormap = self.get_colormap()
        
        self.fillcolor = colormap.alloc_color(
            fillcolor, True, True)
            
        self.bordercolor = colormap.alloc_color(
            bordercolor, True, True)

        self.connect("expose-event", self.expose)
        self.connect("size-allocate", self.size_allocate)

    def update_constants(self):

        if self.alloc == None:
            return

        self.borderW = self.get_border_width()
        self.borderWMUL2 = self.borderW * 2
        self.corner = self.radius + self.borderW
        self.cornerMUL2 = self.corner * 2
        self.cornerMINborderW = self.corner - self.borderW

        self.xPLUborderW = self.alloc.x + self.borderW
        self.xPLUcorner = self.alloc.x + self.corner
        self.xPLUwidthMINborderW = self.alloc.x + self.alloc.width - self.borderW
        self.xPLUwidthMINcorner = self.alloc.x + self.alloc.width - self.corner
        self.yPLUborderW = self.alloc.y + self.borderW
        self.yPLUcorner = self.alloc.y + self.corner
        self.yPLUheightMINborderW = self.alloc.y + self.alloc.height - self.borderW
        self.yPLUheightMINcorner = self.alloc.y + self.alloc.height - self.corner
        self.widthMINborderW = self.alloc.width - self.borderW
        self.widthMINcorner = self.alloc.width - self.corner
        self.widthMINcornerMUL2 = self.alloc.width - self.cornerMUL2
        self.heightMINborderW = self.alloc.height - self.borderW
        self.heightMINcorner = self.alloc.height - self.corner
        self.heightMINborderWMUL2 = self.alloc.height - self.borderWMUL2
        self.heightMINcornerMUL2 = self.alloc.height - self.cornerMUL2

        self.roundX1 = self.alloc.x + self.borderW - 1
        self.roundX2 = self.alloc.x + self.alloc.width - self.corner - self.radius - 1
        self.roundY1 = self.alloc.y + self.borderW - 1
        self.roundY2 = self.alloc.y + self.alloc.height - self.corner - self.radius - 1
        self.roundD = self.radius * 2 + 1
        self.rightAngle = 90 * 64

    def size_allocate(self, widget, allocation):
        self.alloc = allocation
        self.update_constants()
        return False

    def set_border_width(self, width):
        gtk.HBox.set_border_width(self, width)
        self.update_constants()

    def set_radius(self, radius):
        self.radius = radius
        self.update_constants()

    def set_fill_color(self, color):
        colormap = self.get_colormap()
        self.fillcolor = colormap.alloc_color(color, True, True)

    def set_border_color(self, color):
        colormap = self.get_colormap()
        self.bordercolor = colormap.alloc_color(color, True, True)

    def expose(self, widget, event):

        if self.alloc == None:
            return

        #TP.ProfileBegin( "Round*Box::expose" )

        style = self.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]

        startX = event.area.x - self.alloc.x
        startY = event.area.y - self.alloc.y
        stopX = startX + event.area.width
        stopY = startY + event.area.height

        saveForeground = gc.foreground

        # Note: could maybe do some optimization to fill only areas that are within the dirty rect, but drawing
        # seems to be quite fast compared to python code, so just leave it at clipping by each geometry feature

        gc.foreground = self.bordercolor
        
        if self.borderW:
            if stopY > self.corner and startY < self.heightMINcorner:
                if startX < self.borderW:         # draw left border
                    self.window.draw_rectangle(
                        gc, True, self.alloc.x,
                        self.yPLUcorner, self.borderW,
                        self.heightMINcornerMUL2)
                        
                if stopX > self.widthMINborderW:  # draw right border
                    self.window.draw_rectangle(
                        gc, True, self.xPLUwidthMINborderW,
                        self.yPLUcorner, self.borderW,
                        self.heightMINcornerMUL2)

            if stopX > self.corner and startX < self.widthMINcorner:
                if startY < self.borderW:         # draw top border
                    self.window.draw_rectangle(
                        gc, True, self.xPLUcorner, self.alloc.y,
                        self.widthMINcornerMUL2, self.borderW)
                        
                if stopY > self.heightMINborderW: # draw bottom border
                    self.window.draw_rectangle(
                        gc, True, self.xPLUcorner,
                        self.yPLUheightMINborderW,
                        self.widthMINcornerMUL2, self.borderW)

        if startX < self.corner:
            if startY < self.corner:              # draw top left corner
                self.window.draw_rectangle(
                    gc, True, self.alloc.x, self.alloc.y,
                    self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                
                self.window.draw_arc(
                    gc, True, self.roundX1, self.roundY1,
                    self.roundD, self.roundD,
                    self.rightAngle, self.rightAngle)
                    
                gc.foreground = self.bordercolor
                
            if stopY > self.heightMINcorner:      # draw bottom left corner
                self.window.draw_rectangle(
                    gc, True, self.alloc.x,
                    self.yPLUheightMINcorner,
                    self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                
                self.window.draw_arc(
                    gc, True, self.roundX1, self.roundY2,
                    self.roundD, self.roundD, -self.rightAngle,
                    -self.rightAngle)
                    
                gc.foreground = self.bordercolor
                
        if stopX > self.widthMINcorner:
            if startY < self.corner:              # draw top right corner
                self.window.draw_rectangle(
                    gc, True, self.xPLUwidthMINcorner,
                    self.alloc.y, self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                
                self.window.draw_arc(
                    gc, True, self.roundX2, self.roundY1,
                    self.roundD, self.roundD, 0, self.rightAngle)
                    
                gc.foreground = self.bordercolor
                
            if stopY > self.heightMINcorner:      # draw bottom right corner
                self.window.draw_rectangle(
                    gc, True, self.xPLUwidthMINcorner,
                    self.yPLUheightMINcorner, self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                
                self.window.draw_arc(
                    gc, True, self.roundX2, self.roundY2,
                    self.roundD, self.roundD, 0, -self.rightAngle)
                    
                gc.foreground = self.bordercolor

        gc.foreground = self.fillcolor
        
        if startX < self.widthMINcorner and stopX > self.corner:
            if startY < self.heightMINborderW and stopY > self.borderW: # draw centre fill
                self.window.draw_rectangle(
                    gc, True, self.xPLUcorner, self.yPLUborderW,
                    self.widthMINcornerMUL2, self.heightMINborderWMUL2)
                    
        if startX < self.corner and stopX > self.borderW:
            if startY < self.heightMINcorner and stopY > self.corner:   # draw left fill
                self.window.draw_rectangle(
                    gc, True, self.xPLUborderW, self.yPLUcorner,
                    self.cornerMINborderW, self.heightMINcornerMUL2)
                    
        if startX < self.widthMINborderW and stopX > self.widthMINcorner:
            if startY < self.heightMINcorner and stopY > self.corner:   # draw right fill
                self.window.draw_rectangle(gc, True, self.xPLUwidthMINcorner,
                    self.yPLUcorner, self.cornerMINborderW, self.heightMINcornerMUL2)

        gc.foreground = saveForeground
        return False


class RoundVBox(gtk.VBox):
    
    def __init__(self, radius=5,
        fillcolor="#000", bordercolor="#FFF",
        homogeneous=False, spacing=0):
            
        gtk.VBox.__init__(self, homogeneous, spacing)
        
        self.alloc = None

        self.radius = radius

        colormap = self.get_colormap()
        self.fillcolor = colormap.alloc_color(fillcolor, True, True)
        self.bordercolor = colormap.alloc_color(bordercolor, True, True)

        self.connect("expose-event", self.expose)
        self.connect("size-allocate", self.size_allocate)

    def update_constants(self):

        if self.alloc == None:
            return

        self.borderW = self.get_border_width()
        self.borderWMUL2 = self.borderW * 2
        self.corner = self.radius + self.borderW
        self.cornerMUL2 = self.corner * 2
        self.cornerMINborderW = self.corner - self.borderW

        self.xPLUborderW = self.alloc.x + self.borderW
        self.xPLUcorner = self.alloc.x + self.corner
        self.xPLUwidthMINborderW = self.alloc.x + self.alloc.width - self.borderW
        self.xPLUwidthMINcorner = self.alloc.x + self.alloc.width - self.corner
        self.yPLUborderW = self.alloc.y + self.borderW
        self.yPLUcorner = self.alloc.y + self.corner
        self.yPLUheightMINborderW = self.alloc.y + self.alloc.height - self.borderW
        self.yPLUheightMINcorner = self.alloc.y + self.alloc.height - self.corner
        self.widthMINborderW = self.alloc.width - self.borderW
        self.widthMINcorner = self.alloc.width - self.corner
        self.widthMINcornerMUL2 = self.alloc.width - self.cornerMUL2
        self.heightMINborderW = self.alloc.height - self.borderW
        self.heightMINcorner = self.alloc.height - self.corner
        self.heightMINborderWMUL2 = self.alloc.height - self.borderWMUL2
        self.heightMINcornerMUL2 = self.alloc.height - self.cornerMUL2

        self.roundX1 = self.alloc.x + self.borderW - 1
        self.roundX2 = self.alloc.x + self.alloc.width - self.corner - self.radius - 1
        self.roundY1 = self.alloc.y + self.borderW - 1
        self.roundY2 = self.alloc.y + self.alloc.height - self.corner - self.radius - 1
        self.roundD = self.radius * 2 + 1
        self.rightAngle = 90 * 64

    def size_allocate(self, widget, allocation):
        self.alloc = allocation
        self.update_constants()
        return False

    def set_border_width(self, width):
        gtk.VBox.set_border_width(self, width)
        self.update_constants()

    def set_radius(self, radius):
        self.radius = radius
        self.update_constants()

    def set_fill_color(self, color):
        colormap = self.get_colormap()
        self.fillcolor = colormap.alloc_color(color, True, True)

    def set_border_color(self, color):
        colormap = self.get_colormap()
        self.bordercolor = colormap.alloc_color(color, True, True)

    def expose(self, widget, event):

        if self.alloc == None:
            return

        style = self.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]

        startX = event.area.x - self.alloc.x
        startY = event.area.y - self.alloc.y
        stopX = startX + event.area.width
        stopY = startY + event.area.height

        saveForeground = gc.foreground

        # Note: could maybe do some optimization to fill only areas that are within the dirty rect, but drawing
        # seems to be quite fast compared to python code, so just leave it at clipping by each geometry feature

        gc.foreground = self.bordercolor
        if self.borderW:
            if stopY > self.corner and startY < self.heightMINcorner:
                if startX < self.borderW: # draw left border
                    self.window.draw_rectangle(
                        gc, True, self.alloc.x,
                        self.yPLUcorner, self.borderW,
                        self.heightMINcornerMUL2)
                        
                if stopX > self.widthMINborderW: # draw right border
                    self.window.draw_rectangle(
                        gc, True, self.xPLUwidthMINborderW,
                        self.yPLUcorner, self.borderW,
                        self.heightMINcornerMUL2 )

            if stopX > self.corner and startX < self.widthMINcorner:
                if startY < self.borderW: # draw top border
                    self.window.draw_rectangle(
                        gc, True, self.xPLUcorner,
                        self.alloc.y, self.widthMINcornerMUL2,
                        self.borderW)
                        
                if stopY > self.heightMINborderW: # draw bottom border
                    self.window.draw_rectangle(
                        gc, True, self.xPLUcorner,
                        self.yPLUheightMINborderW,
                        self.widthMINcornerMUL2, self.borderW )

        if startX < self.corner:
            if startY < self.corner: # draw top left corner
                self.window.draw_rectangle(
                    gc, True, self.alloc.x,
                    self.alloc.y, self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                self.window.draw_arc(
                    gc, True, self.roundX1,
                    self.roundY1, self.roundD,
                    self.roundD, self.rightAngle,
                    self.rightAngle)
                    
                gc.foreground = self.bordercolor
                
            if stopY > self.heightMINcorner: # draw bottom left corner
                self.window.draw_rectangle(
                    gc, True, self.alloc.x,
                    self.yPLUheightMINcorner,
                    self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                self.window.draw_arc(
                    gc, True, self.roundX1,
                    self.roundY2, self.roundD,
                    self.roundD, -self.rightAngle,
                    -self.rightAngle )
                    
                gc.foreground = self.bordercolor
                
        if stopX > self.widthMINcorner:
            if startY < self.corner: # draw top right corner
                self.window.draw_rectangle(
                    gc, True, self.xPLUwidthMINcorner,
                    self.alloc.y, self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                self.window.draw_arc(
                    gc, True, self.roundX2,
                    self.roundY1, self.roundD,
                    self.roundD, 0, self.rightAngle)
                    
                gc.foreground = self.bordercolor
                
            if stopY > self.heightMINcorner: # draw bottom right corner
                self.window.draw_rectangle(
                    gc, True, self.xPLUwidthMINcorner,
                    self.yPLUheightMINcorner,
                    self.corner, self.corner)
                    
                gc.foreground = self.fillcolor
                self.window.draw_arc(
                    gc, True, self.roundX2,
                    self.roundY2, self.roundD,
                    self.roundD, 0, -self.rightAngle)
                    
                gc.foreground = self.bordercolor

        gc.foreground = self.fillcolor
        
        if startX < self.widthMINcorner and stopX > self.corner:
            if startY < self.heightMINborderW and stopY > self.borderW: # draw centre fill
                self.window.draw_rectangle(
                    gc, True, self.xPLUcorner,
                    self.yPLUborderW, self.widthMINcornerMUL2,
                    self.heightMINborderWMUL2)
                    
        if startX < self.corner and stopX > self.borderW:
            if startY < self.heightMINcorner and stopY > self.corner:   # draw left fill
                self.window.draw_rectangle(
                    gc, True, self.xPLUborderW,
                    self.yPLUcorner, self.cornerMINborderW,
                    self.heightMINcornerMUL2)
                    
        if startX < self.widthMINborderW and stopX > self.widthMINcorner:
            if startY < self.heightMINcorner and stopY > self.corner:   # draw right fill
                self.window.draw_rectangle(
                    gc, True, self.xPLUwidthMINcorner,
                    self.yPLUcorner, self.cornerMINborderW,
                    self.heightMINcornerMUL2 )

        gc.foreground = saveForeground
        return False


class ImageButton(gtk.Button):
    
    def __init__(self, mainImg_path,
        clickImg_path=None, enterImg_path=None,
        backgroundFill=None ):
            
        mainImg_path = imagefile(mainImg_path)
        clickImg_path = imagefile(clickImg_path)
        enterImg_path = imagefile(enterImg_path)

        gtk.Button.__init__(self)
        self.alloc = None
        win = gtk.gdk.get_default_root_window()
        self.gc = gtk.gdk.GC( win )
        self.image = {}
        self.itype = {}
        self.iwidth = {}
        self.iwidthDIV2 = {}
        self.iheight = {}
        self.iheightDIV2 = {}

        self.backgroundFill = backgroundFill

        def prepareImage(name, path):
            
            pix = gtk.gdk.pixbuf_new_from_file(path)
            
            if pix.get_has_alpha():
                if backgroundFill == None:
                    self.image[name] = pix
                    self.itype[name] = ITYPE.PIXBUF
                    
                else:
                    self.image[name] = gtk.gdk.Pixmap(
                        win, pix.get_width(), pix.get_height())
                        
                    colormap = self.get_colormap()
                    self.gc.foreground = colormap.alloc_color(
                        backgroundFill, True, True )
                        
                    self.image[name].draw_rectangle(
                        self.gc, True, 0, 0, pix.get_width(),
                        pix.get_height())
                        
                    self.image[name].draw_pixbuf(
                        self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                        pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                        
                    self.itype[name] = ITYPE.PIXMAP
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                    pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
                
            self.iwidth[name] = pix.get_width()
            self.iwidthDIV2[name] = self.iwidth[name] / 2
            self.iheight[name] = pix.get_height()
            self.iheightDIV2[name] = self.iheight[name] / 2

        prepareImage("main", mainImg_path)

        if enterImg_path != None:
            prepareImage("enter", enterImg_path)
            self.connect('enter-notify-event', self.on_btn_enter)
            self.connect('leave-notify-event', self.on_btn_leave)
            
        if clickImg_path != None:
            prepareImage("click", clickImg_path)
            self.connect('pressed',self.on_btn_press, None)
            self.connect('released',self.on_btn_release, None)
            
            if enterImg_path == None:
                self.image["enter"] = self.image["main"]
                self.itype["enter"] = self.itype["main"]
                self.iwidth["enter"] = self.iwidth["main"]
                self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
                self.iheight["enter"] = self.iheight["main"]
                self.iheightDIV2["enter"] = self.iheightDIV2["main"]
                self.connect('enter-notify-event',self.on_btn_enter)
                self.connect('leave-notify-event',self.on_btn_leave)

        self.curImage = self.upImage = "main"
        self.down = False

        self.connect('expose-event', self.expose)
        self.connect('size-allocate', self.size_allocate)

        self.set_size_request(self.iwidth["main"],
            self.iheight["main"])

    def size_allocate(self, widget, allocation):
        self.alloc = allocation
        self.drawX = allocation.x + allocation.width / 2
        self.drawY = allocation.y + allocation.height / 2

    def expose(self, widget, event):
        
        if self.itype[self.curImage] == ITYPE.PIXBUF:
            self.window.draw_pixbuf(
                self.gc, self.image[self.curImage], 0, 0,
                self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage], self.iheight[self.curImage],
                gtk.gdk.RGB_DITHER_NONE)
                
        else:
            self.window.draw_drawable(
                self.gc, self.image[self.curImage], 0, 0,
                self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage], self.iheight[self.curImage])

        return True
    
    def setImage(self, name, pix):
        
        if name == "main" and self.image["main"] == self.image["enter"]:
            updateEnter = True
            
        else:
            updateEnter = False

        if pix.get_has_alpha():
            if self.backgroundFill == None:
                self.image[name] = pix
                self.itype[name] = ITYPE.PIXBUF
                
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                colormap = self.get_colormap()
                self.gc.foreground = colormap.alloc_color(
                    self.backgroundFill, True, True)
                    
                self.image[name].draw_rectangle(
                    self.gc, True, 0, 0, pix.get_width(),
                    pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                    pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
                
        else:
            self.image[name] = gtk.gdk.Pixmap(
                win, pix.get_width(), pix.get_height())
                
            self.image[name].draw_pixbuf(
                self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                
            self.itype[name] = ITYPE.PIXMAP
            
        self.iwidth[name] = pix.get_width()
        self.iwidthDIV2[name] = self.iwidth[name] / 2
        self.iheight[name] = pix.get_height()
        self.iheightDIV2[name] = self.iheight[name] / 2

        if updateEnter:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]
            self.connect('enter-notify-event',self.on_btn_enter)
            self.connect('leave-notify-event',self.on_btn_leave)

        self.queue_draw()

    def on_btn_press(self, widget, event):
        self.curImage = "click"
        self.down = True
        self.queue_draw()

    def on_btn_enter(self, widget, event):
        
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.upImage = "enter"
            
            if self.down:
                self.curImage = "click"
                
            else:
                self.curImage = "enter"
                
            self.queue_draw()

    def on_btn_leave(self, widget, event):
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.curImage = self.upImage = "main"
            self.queue_draw()

    def on_btn_release(self, widget, event):
        self.curImage = self.upImage
        self.down = False
        self.queue_draw()
        
    def set_palette(self, palette):
        self._palette = palette
        self._palette.props.invoker = WidgetInvoker(self)
        self._palette.props.invoker._position_hint = WidgetInvoker.AT_CURSOR


class ImageToggleButton(gtk.ToggleButton):

    def __init__(self , mainImg_path,
        altImg_path, enterImg_path=None,
        backgroundFill=None):

        mainImg_path = imagefile(mainImg_path)
        altImg_path = imagefile(altImg_path)
        enterImg_path = imagefile(enterImg_path)

        gtk.ToggleButton.__init__(self)
        
        self.alloc = None
        self.within = False
        self.clicked = False

        win = gtk.gdk.get_default_root_window()
        self.gc = gtk.gdk.GC( win )
        self.image = {}
        self.itype = {}
        self.iwidth = {}
        self.iwidthDIV2 = {}
        self.iheight = {}
        self.iheightDIV2 = {}
        
        self.backgroundFill = backgroundFill

        def prepareImage(name, path):
            
            pix = gtk.gdk.pixbuf_new_from_file(path)
            
            if pix.get_has_alpha():
                if backgroundFill == None:
                    self.image[name] = pix
                    self.itype[name] = ITYPE.PIXBUF
                    
                else:
                    self.image[name] = gtk.gdk.Pixmap(
                        win, pix.get_width(), pix.get_height())
                        
                    colormap = self.get_colormap()
                    self.gc.foreground = colormap.alloc_color(
                        backgroundFill, True, True)
                        
                    self.image[name].draw_rectangle(
                        self.gc, True, 0, 0, pix.get_width(),
                        pix.get_height())
                        
                    self.image[name].draw_pixbuf(
                        self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                        pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                        
                    self.itype[name] = ITYPE.PIXMAP
                    
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                    pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
                
            self.iwidth[name] = pix.get_width()
            self.iwidthDIV2[name] = self.iwidth[name] / 2
            self.iheight[name] = pix.get_height()
            self.iheightDIV2[name] = self.iheight[name] / 2

        prepareImage("main", mainImg_path)
        prepareImage("alt", altImg_path)

        if enterImg_path != None:
            prepareImage("enter", enterImg_path)
            
        else:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]

        self.connect('enter-notify-event',self.on_btn_enter)
        self.connect('leave-notify-event',self.on_btn_leave)

        self.connect('toggled',self.toggleImage)
        self.connect('pressed',self.pressed)
        self.connect('released',self.released)
        self.connect('expose-event', self.expose)
        self.connect('size-allocate', self.size_allocate)

        self.set_size_request(self.iwidth["main"],self.iheight["main"])

        self.toggleImage(self)

    def size_allocate(self, widget, allocation):
        self.alloc = allocation
        self.drawX = allocation.x + allocation.width / 2
        self.drawY = allocation.y + allocation.height / 2

    def expose(self, widget, event):
        
        if self.itype[self.curImage] == ITYPE.PIXBUF:
            self.window.draw_pixbuf(
                self.gc, self.image[self.curImage], 0, 0,
                self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage], self.iheight[self.curImage],
                gtk.gdk.RGB_DITHER_NONE)
                
        else:
            self.window.draw_drawable(
                self.gc, self.image[self.curImage], 0, 0,
                self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage], self.iheight[self.curImage])
                
        return True

    def setImage(self, name, pix):
        
        if name == "main" and self.image["main"] == self.image["enter"]:
            updateEnter = True
            
        else:
            updateEnter = False

        if pix.get_has_alpha():
            if self.backgroundFill == None:
                self.image[name] = pix
                self.itype[name] = ITYPE.PIXBUF
                
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                colormap = self.get_colormap()
                
                self.gc.foreground = colormap.alloc_color(
                    self.backgroundFill, True, True)
                
                self.image[name].draw_rectangle(
                    self.gc, True, 0, 0, pix.get_width(),
                    pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                    pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
                
        else:
            self.image[name] = gtk.gdk.Pixmap(
                win, pix.get_width(), pix.get_height())
                
            self.image[name].draw_pixbuf(
                self.gc, pix, 0, 0, 0, 0, pix.get_width(),
                pix.get_height(), gtk.gdk.RGB_DITHER_NONE)
                
            self.itype[name] = ITYPE.PIXMAP
            
        self.iwidth[name] = pix.get_width()
        self.iwidthDIV2[name] = self.iwidth[name] / 2
        self.iheight[name] = pix.get_height()
        self.iheightDIV2[name] = self.iheight[name] / 2

        if updateEnter:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]
            self.connect('enter-notify-event',self.on_btn_enter)
            self.connect('leave-notify-event',self.on_btn_leave)

        self.queue_draw()

    def toggleImage(self, widget):
    
        if not self.get_active():
            if self.within and self.image.has_key("enter"):
                self.curImage = "enter"
                
            else:
                self.curImage = "main"
        else:
            self.curImage = "alt"
            
        self.queue_draw()

    def pressed(self, widget):
        self.clicked = True
        self.curImage = "alt"
        self.queue_draw()

    def released(self, widget):
        self.clicked = False
        self.toggleImage(self)
        
    def on_btn_enter(self, widget, event):
        
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.within = True
            if not self.get_active() and not self.clicked:
                self.curImage = "enter"
                
            else:
                self.curImage = "alt"
                
            self.queue_draw()

    def on_btn_leave(self, widget, event ):
        
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.within = False
            
            if not self.get_active():
                self.curImage = "main"
                
            else:
                self.curImage = "alt"
                
            self.queue_draw()
            
    def set_palette(self, palette):
        self._palette = palette
        self._palette.props.invoker = WidgetInvoker(self)
        self._palette.props.invoker._position_hint = WidgetInvoker.AT_CURSOR


class ImageRadioButton2(gtk.RadioButton):

    def __init__(self, group, mainImg_path,
        altImg_path, enterImg_path=None,
        backgroundFill=None):
            
        mainImg_path = imagefile(mainImg_path)
        altImg_path = imagefile(altImg_path)
        enterImg_path = imagefile(enterImg_path)

        gtk.RadioButton.__init__(self, group)
        
        self.alloc = None
        self.within = False
        self.clicked = False

        win = gtk.gdk.get_default_root_window()
        self.gc = gtk.gdk.GC( win )
        self.image = {}
        self.itype = {}
        self.iwidth = {}
        self.iwidthDIV2 = {}
        self.iheight = {}
        self.iheightDIV2 = {}

        self.backgroundFill = backgroundFill

        def prepareImage(name, path):
        
            pix = gtk.gdk.pixbuf_new_from_file_at_size(path, 95, 95)
            
            if pix.get_has_alpha():
                if backgroundFill == None:
                    self.image[name] = pix
                    self.itype[name] = ITYPE.PIXBUF
                    
                else:
                    self.image[name] = gtk.gdk.Pixmap(
                        win, pix.get_width(), pix.get_height())
                        
                    colormap = self.get_colormap()
                    self.gc.foreground = colormap.alloc_color(
                        backgroundFill, True, True)
                        
                    self.image[name].draw_rectangle(
                        self.gc, True, 0, 0,
                        pix.get_width(), pix.get_height())
                        
                    self.image[name].draw_pixbuf(
                        self.gc, pix, 0, 0, 0, 0,
                        pix.get_width(), pix.get_height(),
                        gtk.gdk.RGB_DITHER_NONE)
                        
                    self.itype[name] = ITYPE.PIXMAP
                    
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0,
                    pix.get_width(), pix.get_height(),
                    gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
                
            self.iwidth[name] = pix.get_width()
            self.iwidthDIV2[name] = self.iwidth[name] / 2
            self.iheight[name] = pix.get_height()
            self.iheightDIV2[name] = self.iheight[name] / 2

        prepareImage("main", mainImg_path)
        prepareImage("alt", altImg_path)

        if enterImg_path != None:
            prepareImage("enter", enterImg_path)
            
        else:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]

        self.connect('enter-notify-event',self.on_btn_enter)
        self.connect('leave-notify-event',self.on_btn_leave)

        self.connect("toggled", self.toggleImage )
        self.connect('pressed',self.pressed )
        self.connect('released',self.released )
        self.connect('expose-event', self.expose)
        self.connect('size-allocate', self.size_allocate)

        self.set_size_request(self.iwidth["main"],self.iheight["main"])

        self.toggleImage( self )

    def size_allocate(self, widget, allocation):
        self.alloc = allocation
        self.drawX = allocation.x + allocation.width / 2
        self.drawY = allocation.y + allocation.height / 2

    def expose(self, widget, event):
    
        if self.itype[self.curImage] == ITYPE.PIXBUF:
            self.window.draw_pixbuf(
                self.gc, self.image[self.curImage],
                0, 0, self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage], self.iheight[self.curImage],
                gtk.gdk.RGB_DITHER_NONE)
                
        else:
            self.window.draw_drawable(
                self.gc, self.image[self.curImage],
                0, 0, self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage],
                self.iheight[self.curImage])
                
        return True

    def setImage(self, name, pix):
    
        if name == "main" and self.image["main"] == self.image["enter"]:
            updateEnter = True
            
        else:
            updateEnter = False

        if pix.get_has_alpha():
            if self.backgroundFill == None:
                self.image[name] = pix
                self.itype[name] = ITYPE.PIXBUF
                
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                colormap = self.get_colormap()
                self.gc.foreground = colormap.alloc_color(
                    self.backgroundFill, True, True)
                    
                self.image[name].draw_rectangle(
                    self.gc, True, 0, 0,
                    pix.get_width(), pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0,
                    pix.get_width(), pix.get_height(),
                    gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
        else:
            self.image[name] = gtk.gdk.Pixmap(
                win, pix.get_width(), pix.get_height())
                
            self.image[name].draw_pixbuf(
                self.gc, pix, 0, 0, 0, 0,
                pix.get_width(), pix.get_height(),
                gtk.gdk.RGB_DITHER_NONE )
                
            self.itype[name] = ITYPE.PIXMAP
            
        self.iwidth[name] = pix.get_width()
        self.iwidthDIV2[name] = self.iwidth[name] / 2
        self.iheight[name] = pix.get_height()
        self.iheightDIV2[name] = self.iheight[name] / 2

        if updateEnter:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]
            self.connect('enter-notify-event',self.on_btn_enter)
            self.connect('leave-notify-event',self.on_btn_leave)

        self.queue_draw()

    def toggleImage(self, widget):
        
        if not self.get_active():
            if self.within and self.image.has_key("enter"):
                self.curImage = "enter"
                
            else:
                self.curImage = "main"
                
        else:
            self.curImage = "alt"
            
        self.queue_draw()

    def pressed(self, widget):
        self.clicked = True
        self.curImage = "alt"
        self.queue_draw()

    def released(self, widget):
        self.clicked = False
        self.toggleImage( self )
        
    def on_btn_enter(self, widget, event):
    
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.within = True
            
            if not self.get_active() and not self.clicked:
                self.curImage = "enter"
                
            else:
                self.curImage = "alt"
                
            self.queue_draw()

    def on_btn_leave(self, widget, event):
    
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.within = False
            
            if not self.get_active():
                self.curImage = "main"
                
            else:
                self.curImage = "alt"
                
            self.queue_draw()
            
    def set_palette(self, palette):
        self._palette = palette
        self._palette.props.invoker = WidgetInvoker(self)
        self._palette.props.invoker._position_hint = WidgetInvoker.AT_CURSOR


class ImageRadioButton(gtk.RadioButton):

    def __init__(self, group, mainImg_path,
        altImg_path, enterImg_path=None,
        backgroundFill=None):
            
        mainImg_path = imagefile(mainImg_path)
        altImg_path = imagefile(altImg_path)
        enterImg_path = imagefile(enterImg_path)

        gtk.RadioButton.__init__(self, group)
        
        self.alloc = None
        self.within = False
        self.clicked = False

        win = gtk.gdk.get_default_root_window()
        self.gc = gtk.gdk.GC( win )
        self.image = {}
        self.itype = {}
        self.iwidth = {}
        self.iwidthDIV2 = {}
        self.iheight = {}
        self.iheightDIV2 = {}

        self.backgroundFill = backgroundFill

        def prepareImage(name, path):
        
            pix = gtk.gdk.pixbuf_new_from_file_at_size(path, 115, 115)
            
            if pix.get_has_alpha():
                if backgroundFill == None:
                    self.image[name] = pix
                    self.itype[name] = ITYPE.PIXBUF
                    
                else:
                    self.image[name] = gtk.gdk.Pixmap(
                        win, pix.get_width(), pix.get_height())
                        
                    colormap = self.get_colormap()
                    self.gc.foreground = colormap.alloc_color(
                        backgroundFill, True, True)
                        
                    self.image[name].draw_rectangle(
                        self.gc, True, 0, 0,
                        pix.get_width(), pix.get_height())
                        
                    self.image[name].draw_pixbuf(
                        self.gc, pix, 0, 0, 0, 0,
                        pix.get_width(), pix.get_height(),
                        gtk.gdk.RGB_DITHER_NONE)
                        
                    self.itype[name] = ITYPE.PIXMAP
                    
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0,
                    pix.get_width(), pix.get_height(),
                    gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
                
            self.iwidth[name] = pix.get_width()
            self.iwidthDIV2[name] = self.iwidth[name] / 2
            self.iheight[name] = pix.get_height()
            self.iheightDIV2[name] = self.iheight[name] / 2

        prepareImage("main", mainImg_path)
        prepareImage("alt", altImg_path)

        if enterImg_path != None:
            prepareImage("enter", enterImg_path)
            
        else:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]

        self.connect('enter-notify-event',self.on_btn_enter)
        self.connect('leave-notify-event',self.on_btn_leave)

        self.connect("toggled", self.toggleImage )
        self.connect('pressed', self.pressed )
        self.connect('released', self.released )
        self.connect('expose-event', self.expose)
        self.connect('size-allocate', self.size_allocate)

        self.set_size_request(self.iwidth["main"], self.iheight["main"])

        self.toggleImage( self )

    def size_allocate(self, widget, allocation):
        self.alloc = allocation
        self.drawX = allocation.x + allocation.width / 2
        self.drawY = allocation.y + allocation.height / 2

    def expose(self, widget, event):
    
        if self.itype[self.curImage] == ITYPE.PIXBUF:
            self.window.draw_pixbuf(
                self.gc, self.image[self.curImage],
                0, 0, self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage], self.iheight[self.curImage],
                gtk.gdk.RGB_DITHER_NONE)
                
        else:
            self.window.draw_drawable(
                self.gc, self.image[self.curImage],
                0, 0, self.drawX - self.iwidthDIV2[self.curImage],
                self.drawY - self.iheightDIV2[self.curImage],
                self.iwidth[self.curImage],
                self.iheight[self.curImage])
                
        return True

    def setImage(self, name, pix):
    
        if name == "main" and self.image["main"] == self.image["enter"]:
            updateEnter = True
            
        else:
            updateEnter = False

        if pix.get_has_alpha():
            if self.backgroundFill == None:
                self.image[name] = pix
                self.itype[name] = ITYPE.PIXBUF
                
            else:
                self.image[name] = gtk.gdk.Pixmap(
                    win, pix.get_width(), pix.get_height())
                    
                colormap = self.get_colormap()
                self.gc.foreground = colormap.alloc_color(
                    self.backgroundFill, True, True)
                    
                self.image[name].draw_rectangle(
                    self.gc, True, 0, 0,
                    pix.get_width(), pix.get_height())
                    
                self.image[name].draw_pixbuf(
                    self.gc, pix, 0, 0, 0, 0,
                    pix.get_width(), pix.get_height(),
                    gtk.gdk.RGB_DITHER_NONE)
                    
                self.itype[name] = ITYPE.PIXMAP
        else:
            self.image[name] = gtk.gdk.Pixmap(
                win, pix.get_width(), pix.get_height())
                
            self.image[name].draw_pixbuf(
                self.gc, pix, 0, 0, 0, 0,
                pix.get_width(), pix.get_height(),
                gtk.gdk.RGB_DITHER_NONE )
                
            self.itype[name] = ITYPE.PIXMAP
            
        self.iwidth[name] = pix.get_width()
        self.iwidthDIV2[name] = self.iwidth[name] / 2
        self.iheight[name] = pix.get_height()
        self.iheightDIV2[name] = self.iheight[name] / 2

        if updateEnter:
            self.image["enter"] = self.image["main"]
            self.itype["enter"] = self.itype["main"]
            self.iwidth["enter"] = self.iwidth["main"]
            self.iwidthDIV2["enter"] = self.iwidthDIV2["main"]
            self.iheight["enter"] = self.iheight["main"]
            self.iheightDIV2["enter"] = self.iheightDIV2["main"]
            self.connect('enter-notify-event',self.on_btn_enter)
            self.connect('leave-notify-event',self.on_btn_leave)

        self.queue_draw()

    def toggleImage( self, widget ):
        
        if not self.get_active():
            if self.within and self.image.has_key("enter"):
                self.curImage = "enter"
                
            else:
                self.curImage = "main"
                
        else:
            self.curImage = "alt"
            
        self.queue_draw()

    def pressed( self, widget ):
        self.clicked = True
        self.curImage = "alt"
        self.queue_draw()

    def released( self, widget ):
        self.clicked = False
        self.toggleImage( self )
        
    def on_btn_enter(self, widget, event):
    
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.within = True
            
            if not self.get_active() and not self.clicked:
                self.curImage = "enter"
                
            else:
                self.curImage = "alt"
                
            self.queue_draw()

    def on_btn_leave(self, widget, event):
    
        if event.mode == gtk.gdk.CROSSING_NORMAL:
            self.within = False
            
            if not self.get_active():
                self.curImage = "main"
                
            else:
                self.curImage = "alt"
                
            self.queue_draw()
            
    def set_palette(self, palette):
        self._palette = palette
        self._palette.props.invoker = WidgetInvoker(self)
        self._palette.props.invoker._position_hint = WidgetInvoker.AT_CURSOR


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
