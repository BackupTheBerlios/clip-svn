from PyQt4 import QtCore, QtGui
from Ui_LauePlaneCfgUI import Ui_LauePlaneCfgUI
import math



class LauePlaneCfg(QtGui.QWidget, Ui_LauePlaneCfgUI):
    def __init__(self,  p,  parent):
        QtGui.QWidget.__init__(self,  parent)
        self.projector=p
        self.setupUi(self)
        
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQDisplay)
        self.connect(self.detMinQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs)
        self.connect(self.detMaxQ,  QtCore.SIGNAL('valueChanged(double)'), self.updateQs)
        
        self.detMinQ.setValue(self.projector.Qmin())
        self.detMaxQ.setValue(self.projector.Qmax())
        
    def updateQDisplay(self, d):
        self.QDispA.setValue(2.0*math.pi/d)
        self.QDispKEV.setValue(0.5*12.398*d/math.pi)
        
    def updateQs(self):
        self.projector.setWavevectors(self.detMinQ.value(), self.detMaxQ.value())
