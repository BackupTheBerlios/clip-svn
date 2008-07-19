from PyQt4 import QtCore, QtGui
from Ui_ReflexInfo import Ui_ReflexInfo
from Tools import parseHKL
from ToolBox import Vec3D, Mat3D, Projector
from ToolWidget import ToolWidget
import math



class ReflexInfo(ToolWidget, Ui_ReflexInfo):
    def __init__(self, parent=None):
        ToolWidget.__init__(self, 'Reflexinfo', parent)
        self.setupUi(self)

    def windowChanged(self):
        self.updateDisplay()
        
    def orientationChanged(self):
        self.updateDisplay()
        
    def updateDisplay(self):
        c=self.searchCrystal()
        if c:
            hkl=parseHKL(str(self.reflex.text()))
            if hkl:
                h, k, l=hkl
                v=c.hkl2Reziprocal(h, k, l)
                Q=v.norm()
                self.infoQ.setText('%.2f'%Q)
                if Q>0.0:
                    d=1.0/Q
                    self.infoD.setText('%.2f'%d)
                    v*=d
                    v2, b=Projector.normal2scattered(v)
                    if b:
                        self.info2T.setText('%.2f'%(180.0-math.degrees(math.acos(v2.x()))))
                    else:
                        self.info2T.setText('')
                    for n, w1, w2 in ((0, self.axX, self.axMX), (1, self.axY, self.axMY), (2, self.axZ, self.axMZ)):
                        ang=math.degrees(math.acos(max(-1, min(1, v[n]))))
                        w1.setText('%.2f'%ang)
                        w2.setText('%.2f'%(180.0-ang))
                        
                self.diffOrders.setText('')
                for r in c.getReflectionList():
                    if r.h==h and r.k==k and r.l==l:
                        t=''
                        for n in r.orders:
                            if n>=r.lowestDiffOrder and n<=r.highestDiffOrder:
                                t+='%i, '%n
                        if len(t)>0:
                            self.diffOrders.setText(t[:-2])
                        break
            
    def reflexInfo(self, h, k, l):
        self.reflex.setText('%i %i %i'%(h, k, l))
        self.updateDisplay()
