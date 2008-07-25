from PyQt4 import QtCore, QtGui
from Ui_StereoCfg import Ui_StereoCfg
from ToolBox import Vec3D, Mat3D
import math



class StereoCfg(QtGui.QWidget, Ui_StereoCfg):
    def __init__(self, p, v, parent):
        QtGui.QWidget.__init__(self,  parent)
        self.projector=p
        self.gView=v
        self.setupUi(self)
        
        self.renderCheckboxes=((self.renderAntialias,  QtGui.QPainter.Antialiasing), (self.renderAntialiasText,  QtGui.QPainter.TextAntialiasing)) 

        self.loadParameters()
        
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQDisplay)
        self.connect(self.detMinQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs, QtCore.Qt.QueuedConnection)
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs, QtCore.Qt.QueuedConnection)
        
        for c, v in self.renderCheckboxes:
            self.connect(c, QtCore.SIGNAL('stateChanged(int)'),  self.updateRenderHints)
        
        self.connect(self.maxRefLabel, QtCore.SIGNAL('valueChanged(int)'),  self.updateMaxRefLabel);
        self.connect(self.detTextSize, QtCore.SIGNAL('valueChanged(double)'),  self.projector.setTextSize);
        self.connect(self.detSpotSize, QtCore.SIGNAL('valueChanged(double)'),  self.projector.setSpotSize);
        
        self.connect(self.projector, QtCore.SIGNAL('projectionParamsChanged()'), self.loadParameters)
        self.bGroup=QtGui.QButtonGroup()
        for id, b in enumerate((self.Xp, self.Xm, self.Yp, self.Ym, self.Zp, self.Zm)):
            self.bGroup.addButton(b, id)
        
        self.connect(self.bGroup, QtCore.SIGNAL('buttonClicked(int)'), self.setOrientation)

    def loadParameters(self):
        for a, b in ((self.maxRefLabel, self.projector.getMaxHklSqSum), (self.detTextSize, self.projector.getTextSize), (self.detSpotSize, self.projector.getSpotSize)):
            a.setValue(b())
            
        self.detMinQ.setValue(2.0*math.pi*self.projector.Qmin())
        self.detMaxQ.setValue(2.0*math.pi*self.projector.Qmax())
                
        for c, v in self.renderCheckboxes:
            c.setChecked((self.gView.renderHints()&v)==v)

    def updateQDisplay(self, d):
        if d>0:
            self.QDispA.setValue(2.0*math.pi/d)
            self.QDispKEV.setValue(0.5*12.398*d/math.pi)
        
    def updateQs(self):
        s=0.5/math.pi
        self.projector.setWavevectors(s*self.detMinQ.value(), s*self.detMaxQ.value())
        
    def updateRenderHints(self):
        for c, v in self.renderCheckboxes:
            self.gView.setRenderHint(v, c.isChecked())
        self.gView.resetCachedContent()
        self.gView.viewport().update()
        
    def updateMaxRefLabel(self,  i):
        self.projector.setMaxHklSqSum(i);
        
    def setOrientation(self, i):
        print i
        v1=Vec3D()
        v1[i/2]=1-(i%2)*2
        i=(i+2)%6
        v2=Vec3D()
        v2[i/2]=1-(i%2)*2
        v3=v1%v2
        print v1
        print v2
        print v3
        M=Mat3D(v1, v2, v3).transposed()
        print M*Vec3D(1, 2, 3)
        self.projector.setDetOrientation(M)
        
