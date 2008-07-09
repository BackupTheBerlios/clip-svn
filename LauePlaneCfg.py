from PyQt4 import QtCore, QtGui
from Ui_LauePlaneCfg import Ui_LauePlaneCfg
import math



class LauePlaneCfg(QtGui.QWidget, Ui_LauePlaneCfg):
    def __init__(self, p, v, parent):
        QtGui.QWidget.__init__(self,  parent)
        self.projector=p
        self.gView=v
        self.setupUi(self)
        
        self.renderCheckboxes=((self.renderAntialias,  QtGui.QPainter.Antialiasing), (self.renderAntialiasText,  QtGui.QPainter.TextAntialiasing)) 

        self.loadParameters()

        for a in (self.detDist, self.detWidth, self.detHeight):
            self.connect(a, QtCore.SIGNAL('valueChanged(double)'), self.updateDetSize, QtCore.Qt.QueuedConnection)
            
        for a in (self.detOmega, self.detChi, self.detPhi):
            self.connect(a, QtCore.SIGNAL('valueChanged(double)'), self.updateDetOrientation, QtCore.Qt.QueuedConnection)
        
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQDisplay)
        self.connect(self.detMinQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs, QtCore.Qt.QueuedConnection)
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs, QtCore.Qt.QueuedConnection)
        
        for c, v in self.renderCheckboxes:
            self.connect(c, QtCore.SIGNAL('stateChanged(int)'),  self.updateRenderHints)
        
        self.connect(self.maxRefLabel, QtCore.SIGNAL('valueChanged(int)'),  self.updateMaxRefLabel);
        self.connect(self.detTextSize, QtCore.SIGNAL('valueChanged(double)'),  self.projector.setTextSize);
        self.connect(self.detSpotSize, QtCore.SIGNAL('valueChanged(double)'),  self.projector.setSpotSize);
        self.connect(self.detSpotsEnabled, QtCore.SIGNAL('clicked(bool)'),  self.projector.enableSpots);
        
        self.connect(self.projector, QtCore.SIGNAL('projectionParamsChanged()'), self.loadParameters)
        
        

    def loadParameters(self):
        for a, b in ((self.detDist,  self.projector.dist),  (self.detWidth,  self.projector.width), (self.detHeight, self.projector.height), (self.detOmega,  self.projector.omega),  (self.detChi,  self.projector.chi), (self.detPhi, self.projector.phi), (self.maxRefLabel, self.projector.getMaxHklSqSum), (self.detTextSize, self.projector.getTextSize), (self.detSpotSize, self.projector.getSpotSize)):
            a.setValue(b())
            
        self.detSpotsEnabled.setChecked(self.projector.spotsEnabled())
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
        
    def updateDetSize(self):
        self.projector.setDetSize(*[w.value() for w in (self.detDist,  self.detWidth, self.detHeight)])
        
    def updateDetOrientation(self):
        self.projector.setDetOrientation(*[w.value() for w in (self.detOmega,  self.detChi, self.detPhi)])        
        
    def updateMaxRefLabel(self,  i):
        self.projector.setMaxHklSqSum(i);
