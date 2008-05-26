import Image
import ImageFile
import ImageQt
import scipy
import os
import sys
sys.path.append('Tools')
from BezierCurve import BezierCurve
from PyQt4 import QtGui,  QtCore
from copy import copy
from ToolBox import ImageTransfer



class LaueImage(QtGui.QWidget):
    def __init__(self,  parent,  _name):
        QtGui.QWidget.__init__(self,  parent)
        self.name=os.path.split(_name)[1]
        self.fullImg=Image.open(_name)
        self.VRGB_BezierParams=[[], [], [], []]
        initParams=[[(0, 0),  (1, 1)], 
                 [(0, 0),  (1, 1)], 
                 [(0, 0),  (1, 1)], 
                 [(0, 0),  (1, 1)]]
        
        
        print 'create ImageTransfer'
        self.transfer=ImageTransfer()
        print 'done'
        self.resize(self.size())
        self.setTransferCurves(initParams)
        
    def resizeEvent(self,  e):
        print 'resizeEvent'
        #QtGui.QWidget.resizeEvent(self,  e)
        self.resize(e.size())
    
    def resize(self,  size):
        print 'resize to %ix%i = %i'%(size.width(), size.height(), size.width()*size.height())
        self.scaledImg=self.fullImg.resize((size.width(),  size.height()))
        print 'set'
        self.transfer.setData(size.width(),  size.height(), 0, self.scaledImg.tostring())
        print 'OK'
    
    
    def paintEvent(self, e):
        p=QtGui.QPainter(self)
        print 'about to draw'
        p.drawImage(0, 0, self.transfer.qImg())
        print 'drawn'
        
    def setTransferCurves(self, newParams):
        curvesChanged=False
        for i, pa in enumerate(zip(newParams,  self.VRGB_BezierParams)):
            pn,po=pa
            if pn!=po:
                self.VRGB_BezierParams[i]=pn
                curvesChanged=True

        if curvesChanged:
            for i in range(4):
                c=BezierCurve(*zip(*self.VRGB_BezierParams[i]))
                p1=c.x[1:]
                p2=reduce(lambda x, y:x+y, c.D)
                print 'before setTransferCurve',  p1, p2
                self.transfer.setTransferCurve(i, p1,  p2)
                print 'OK'
            self.update()







class FujiBASImageFile(ImageFile.ImageFile):
    format = "BAS"
    format_description = "Fuji BAS Reader Image Plate format"
     
    def _open(self):
        # Check if we already opened inf:
        magic=self.fp.read(14)
        self.fp.seek(0)
        if magic=='BAS_IMAGE_FILE':
            self.infFile=self.fp
            for ext in ('img',  'IMG'):
                try:
                    self.imgFile=open(self.fp.name[:-3]+ext,  'rb')
                    break
                except:
                    pass
        else:
            self.imgFile=self.fp
            for ext in ('inf',  'INF'):
                try:
                    self.infFile=open(self.fp.name[:-3]+ext)
                    magic=self.infFile.read(14)
                    if magic=='BAS_IMAGE_FILE':
                        self.inf.seek(0)
                        break
                except:
                    pass
        # check header
        if magic!='BAS_IMAGE_FILE':
            raise SyntaxError, "not a FujiBAS file"

        if not self.imgFile:
            raise SyntaxError,  "IMG File not found???"
        
        self.fp=self.imgFile
        
        self.header = self.infFile.readlines()
        self.resx=int(self.header[3])
        self.resy=int(self.header[4])
        self.bpp=int(self.header[5])
        self.width=int(self.header[6])
        self.height=int(self.header[7])
        self.sensitivity=int(self.header[8])
        self.latitude=int(self.header[9])
        self.date=self.header[10]
        self.gesCounts=int(self.header[11])
        
        # size in pixels (width, height)
        self.size = (self.width,  self.height)
        
        if os.stat(self.imgFile.name)[6]!=self.width*self.height*2:
            raise SyntaxError,  "IMG doesnt have correct size"
        
        
        self.mode = "F"

        # data descriptor
        self.tile = [
            ("raw", (0, 0) + self.size, 0, ('F;16B', 0, 1))
        ]

Image.register_open("BAS", FujiBASImageFile)
Image.register_extension("BAS", ".inf")
Image.register_extension("BAS", ".img") 


