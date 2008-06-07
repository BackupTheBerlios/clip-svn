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
        
        
        self.transfer=ImageTransfer()
        self.resizeImg(self.size())
        self.setTransferCurves(initParams)
        sp=self.sizePolicy()
        #sp.setHeightForWidth(True)
        sp.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        sp.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(sp)
        
    def resizeEvent(self,  e):
        #QtGui.QWidget.resizeEvent(self,  e)
        self.resizeImg(e.size())
            
    def resizeImg(self,  size):        
        s=QtCore.QSize(self.fullImg.width,  self.fullImg.height)
        s.scale(size,  QtCore.Qt.KeepAspectRatio)
        print 'Size',self.width(),  self.height() ,  s.width(),  s.height() 

        self.scaledImg=self.fullImg.resize((s.width(),  s.height()))
        mode=None
        if self.scaledImg.mode=='RGB':
            mode=1
        elif self.scaledImg.mode=='F':
            mode=0
        if mode!=None:
            self.transfer.setData(s.width(),  s.height(), mode, self.scaledImg.tostring())
    
    
    def paintEvent(self, e):
        p=QtGui.QPainter(self)
        l=min(self.widht(),  self.height())
        p.translate(0.5*self.width(), 0.5*self.height())
        p.setPen(QtCore.Qt.black)
        p.drawRect(QtCore.QRectF(-0.5*l, -0.5*l, l, l))
        s=self.transfer.qImg().size()
        x=(self.width()-s.width())/2
        y=(self.height()-s.height())/2
        p.drawImage(x, y, self.transfer.qImg())
        
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
                self.transfer.setTransferCurve(i, p1,  p2)
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


