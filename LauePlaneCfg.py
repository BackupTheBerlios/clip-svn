from PyQt4 import QtCore, QtGui
from Ui_LauePlaneCfgUI import Ui_LauePlaneCfgUI
import math



class LauePlaneCfg(QtGui.QWidget, Ui_LauePlaneCfgUI):
    def __init__(self,  p, v, parent):
        QtGui.QWidget.__init__(self,  parent)
        self.projector=p
        self.gView=v
        self.setupUi(self)
        
        for a, b in ((self.detDist,  p.dist),  (self.detWidth,  p.width), (self.detHeight, p.height)):
            a.setValue(b())
            self.connect(a, QtCore.SIGNAL('valueChanged(double)'), self.updateDetSize)
            
        for a, b in ((self.detOmega,  p.omega),  (self.detChi,  p.chi), (self.detPhi, p.phi)):
            a.setValue(b())
            self.connect(a, QtCore.SIGNAL('valueChanged(double)'), self.updateDetOrientation)
        
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQDisplay)
        self.connect(self.detMinQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs)
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs)
        self.detMinQ.setValue(2.0*math.pi*self.projector.Qmin())
        self.detMaxQ.setValue(2.0*math.pi*self.projector.Qmax())


        self.renderCheckboxes=((self.renderAntialias,  QtGui.QPainter.Antialiasing), (self.renderAntialiasText,  QtGui.QPainter.TextAntialiasing))        
        for c, v in self.renderCheckboxes:
            c.setChecked((self.gView.renderHints()&v)==v)
            self.connect(c, QtCore.SIGNAL('stateChanged(int)'),  self.updateRenderHints)
        
        self.maxRefLabel.setValue(self.projector.getMaxHklSqSum())
        self.connect(self.maxRefLabel, QtCore.SIGNAL('valueChanged(int)'),  self.updateMaxRefLabel);
        
        self.detTextSize.setValue(self.projector.getTextSize())
        self.connect(self.detTextSize, QtCore.SIGNAL('valueChanged(double)'),  self.projector.setTextSize);

        self.detSpotSize.setValue(self.projector.getSpotSize())
        self.connect(self.detSpotSize, QtCore.SIGNAL('valueChanged(double)'),  self.projector.setSpotSize);

        self.detSpotsEnabled.setChecked(self.projector.spotsEnabled())
        self.connect(self.detSpotsEnabled, QtCore.SIGNAL('clicked(bool)'),  self.projector.enableSpots);

    def updateQDisplay(self, d):
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
