#!/usr/bin/python3.4

import os.path

from p_image import ImageObject as image

class FileObject:
    """handle the file, open and close it, dispatch to image or svg modules."""
    # This are links to other class used by the main program.
    # These are class attributes.
    # That way when closing a file, attributes are cleared but those stays
    ser = None
    cfg = None
    jsp = None
    wm = None
    im_ext = ('bmp', 'gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff')
    vect_ext = ('svg', )

    def __init__(self):
        self.uri = None
        self.type = None

    def open(self, uri):
        """Open a file.
        Test the type of extension, dispatch to image or vector module."""

        (self.path, self.ext) = os.path.splitext(uri)
        self.ext = self.ext.lstrip('.')

        if self.ext in FileObject.im_ext:
            self.type = 0
            self.im = image()
            self.im.open_file(uri)
        elif self.ext in FileObject.vect_ext:
            self.type = 1
            return False
        else:
            FileObject.wm.message_erreur('Format non pris en charge.',
                                         'Le fichier doit être une image matricielle (bmp, jpg, jpeg, png)\
                                         ou vectorielle (svg).')
            return False
        self.uri = uri

        return True


    def close(self):
        """Close the file. Print info to GUI, clear instance attributes."""
        FileObject.wm.status("Pas d'image chargée", 'file')
        for item in self.__dict__:
            self.__setattr__(item, None)

    def get_pixbuf(self):
        pass

    def compute_file(self):
        pass