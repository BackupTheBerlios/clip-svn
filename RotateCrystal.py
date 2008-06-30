from Ui_RotateCrystal import Ui_RotateCrystal
from PyQt4 import QtCore,  QtGui
from ToolBox import Crystal,  Vec3D,  Mat3D
import math
from Tools import parseHKL
from ToolWidget import ToolWidget


class RotateCrystal(ToolWidget, Ui_RotateCrystal):
    def __init__(self,  parent=None):
        ToolWidget.__init__(self, parent)
        self.setupUi(self)
        self.connect(self.axisChooser,  QtCore.SIGNAL('activated(int)'),  self.indexChanged)
        self.connect(self.axisEdit,  QtCore.SIGNAL('editingFinished()'),  self.indexChanged)
        self.indexChanged()
        bgroup=QtGui.QButtonGroup(self)
        bgroup.setExclusive(False)
        bgroup.addButton(self.butArbPos,  10)
        bgroup.addButton(self.but5Pos,  5)
        bgroup.addButton(self.but1Pos,  1)
        bgroup.addButton(self.but1Neg,  -1)
        bgroup.addButton(self.but5Neg,  -5)
        bgroup.addButton(self.butArbNeg,  -10)
        self.connect(bgroup,  QtCore.SIGNAL('buttonClicked(int)'),  self.addRotation)
        self.connect(self.resetButton,  QtCore.SIGNAL('clicked()'),  self.resetSum)
        self.angSum=0.0
        self.lastcrystal=None
        self.indexChanged()
        
    def windowChanged(self):
        if (self.lastcrystal!=self.searchCrystal()):
            self.resetSum()
            self.loadAxisFromCrystal()
            
    def rotAxisChanged(self):    
        #emitted from crystal
        self.resetSum()
        self.loadAxisFromCrystal()
        
    def projectorAddedRotation(self, a):
        self.angSum+=math.degrees(a)
        self.angSumDisplay.setText('%.2f'%self.angSum)
        
    def resetSum(self):
        self.angSum=0.0
        self.angSumDisplay.setText('%.2f'%self.angSum)
        
    def addRotation(self,  ang):
        c=self.searchCrystal()
        if c:
            if ang in (-10, 10):
                ang=0.1*ang*self.arbAngle.value()
            self.angSum+=ang
            while self.angSum>360:
                self.angSum-=360
            while self.angSum<-360:
                self.angSum+=360
            axis=c.getLabSystamRotationAxis()
            R=Mat3D(axis,  math.radians(ang))
            c.addRotation(R)
            self.angSumDisplay.setText('%.2f'%self.angSum)
        
    def indexChanged(self):
        index=self.axisChooser.currentIndex()
        if (self.axisEdit.isVisible() ^ (index>=3)):
            self.axisEdit.setVisible(index>=3)
            self.update()
        
        axis=None
        if index in (0, 1, 2):
            axis=Vec3D(0, 0, 0)
            axis[index]=1
        elif index in (3, 4, 5):
            s=str(self.axisEdit.text())
            axis=parseHKL(s)
        c=self.searchCrystal()
        if c and axis:
            axis=Vec3D(axis)
            if index in (0, 1, 2, 3):
                c.setRotationAxis(axis, Crystal.LabSystem)
            elif index==4:
                c.setRotationAxis(axis, Crystal.DirectSpace)
            elif index==5:
                c.setRotationAxis(axis, Crystal.ReziprocalSpace)
                
    def loadAxisFromCrystal(self):
        c=self.searchCrystal()
        if c:
            self.lastcrystal=c
            if c.getRotationAxisType()==Crystal.LabSystem:
                v=c.getRotationAxis()
                if v==Vec3D(1, 0, 0):
                    self.axisChooser.setCurrentIndex(0)
                elif v==Vec3D(0, 1, 0):
                    self.axisChooser.setCurrentIndex(1)
                elif v==Vec3D(0, 0, 1):
                    self.axisChooser.setCurrentIndex(2)
                else:
                    self.axisChooser.setCurrentIndex(3)
            elif c.getRotationAxisType()==Crystal.ReziprocalSpace:
                self.axisChooser.setCurrentIndex(4)
            elif c.getRotationAxisType()==Crystal.DirectSpace:
                self.axisChooser.setCurrentIndex(5)
            v=c.getRotationAxis()
            l=[('%.10f'%x).rstrip('0') for x in v]
            l=[x.rstrip('.') for x in l]
            #n=max([len(x)-x.rfind('.') for x in l])
            #format='%%.%if'%(n-1)
            #format=format+' '+format+' '+format
            self.axisEdit.setText(' '.join(l))
                
            
            
        

        

        
