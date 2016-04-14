from PIL import Image

import array

from gi.repository import GdkPixbuf
from gi.repository import Gdk

class Image():
    im = Image.new('RGB', (20,20))
    #This function deals with openning a new file
    def openFile(uri):
        #try to open the file, else give an Error message
        try:
            im = Image.open(uri)
        except IOError:
            wm.messageErreur('Veuillez choisir un fichier image',
                             'Fichiers pris en charge: bmp, jpg, png, tiff, svg')
            return False
        #display status
        wm.status('open %s' %uri)
        #Load the image, get its size, create thumbnail
        im.load()
        w,h = im.size
        thumb = im
        thumb.thumbnail((450, int(450*h/w)))
        #sets the thumbnail in the image area, through the imageToPixbuf function
        wm.image.set_from_pixbuf(imageToPixbuf(thumb))
        return True
    
    #this function close the file that is opened
    def closeFile():
        wm.image.set_from_icon_name(Gtk.STOCK_MISSING_IMAGE, 6)
    
    #this function converts PIL images to Pixbuf format for displaying in Gtk
    def imageToPixbuf(im):
        #transforms the given image into an array of pixels
        arr = array.array('B', im.tostring())
        w,h=im.size
        #look at a an alpha mask
        if im.mode == 'RGBA':
            hasAlpha = True
            dist = w*4
        else:
            hasAlpha = False
            dist = w*3
        #returns the pix buf. Args:
        #array, colorspace, has alpha, bits per sample,
        #width, height, distance in bytes between row starts
        return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB, hasAlpha, 8, w, h, dist)
