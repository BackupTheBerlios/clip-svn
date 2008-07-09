from PyQt4 import QtCore, QtGui
from Ui_ReflexInfo import Ui_ReflexInfo
from Tools import parseHKL
from ToolBox import Vec3D, Mat3D
from ToolWidget import ToolWidget
import math


class ReflexInfo(ToolWidget, Ui_ReflexInfo):
    def __init__(self, parent=None):
        ToolWidget.__init__(self, parent)
        self.setupUi(self)

    def windowChanged(self):
        self.updateDisplay()
        
    def updateDisplay(self):
        c=self.searchCrystal()
        if c:
            hkl=parseHKL(str(self.reflex.text()))
            if hkl:
                h, k, l=hkl
                v=c.hkl2Reziprocal(h, k, l)
                Q=v.norm()
                d=1.0/Q
                v*=d
                for n, w1, w2 in ((0, self.axX, self.axMX), (1, self.axY, self.axMY), (2, self.axZ, self.axMZ)):
                    ang=math.degrees(math.acos(max(-1, min(1, v[n]))))
                    w1.setText('%.2f'%ang)
                    w2.setText('%.2f'%(180.0-ang))
            
    def axisFromReflexInfo(self, h, k, l):
        self.reflex.setText('%i %i %i'%(h, k, l))
        self.updateDisplay()
