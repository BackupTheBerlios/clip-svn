from PyQt4 import QtCore, QtGui
from Ui_Reorient import Ui_Reorient
from Tools import parseHKL
from ToolBox import Vec3D, Mat3D
from Tools.GonioRotator import calcAngles
from ToolWidget import ToolWidget
import math


class Reorient(ToolWidget, Ui_Reorient):
    def __init__(self, parent=None):
        ToolWidget.__init__(self, parent)
        self.axis1Changed=lambda idx: self.axisChanged(idx, 0)
        self.axis2Changed=lambda idx: self.axisChanged(idx, 1)

        self.setupUi(self)

        self.axisCombos=[self.axis1Combo, self.axis2Combo]
        self.axisEdits=[self.axis1Edit, self.axis2Edit]
        self.axisVectors=[None,  None]
        
        for i in range(2):
            self.axisChanged(self.axisCombos[i].currentIndex(), i)
        
    def windowChanged(self):
        self.updateDisplay()
        
    def parseAxis(self,  s,  rezi):
        r=parseHKL(str(s))
        c=self.searchCrystal()
        if r and c:
            if rezi:
                r=c.getReziprocalOrientationMatrix()*r
            else:
                r=c.getRealOrientationMatrix()*r
            r=c.getRotationMatrix()*r
            return r.normalized()
        return None
    
    def fromVect(self):
        return self.parseAxis(self.fromEdit.text(), self.RezicheckBox.isChecked())
    
    def toChanged(self,  idx):
        self.toEdit.setEnabled(idx>2)
        self.toEdit.setVisible(idx>2)
        self.updateDisplay()
        
    def toVect(self):
        idx=self.toCombo.currentIndex()
        if idx>2:
            return self.parseAxis(self.toEdit.text(), idx==3)
        else:
            axis=Vec3D(0, 0, 0)
            axis[idx]=1
        return axis
        
    def toEditChanged(self):
        self.updateDisplay()
        
    def axisChanged(self, idx, axisNr):
        self.axisEdits[axisNr].setEnabled(idx>2)
        self.axisEdits[axisNr].setVisible(idx>2)
        if (idx<3) and (idx==self.axisCombos[1-axisNr].currentIndex()):
            self.axisCombos[1-axisNr].setCurrentIndex((idx+1)%3)
        if idx==3:
            axis=parseHKL(str(self.axisEdits[axisNr].text()))
            if axis:
                self.axisVectors[axisNr]=axis.normalized()
            else:
                self.axisVectors[axisNr]=None
        else:
            self.axisVectors[axisNr]=Vec3D(0, 0, 0)
            self.axisVectors[axisNr][idx]=1
        self.updateDisplay()
        
    def axis1EditChanged(self):
        self.axisChanged(3,  0)
        self.updateDisplay()
        
    def axis2EditChanged(self):
        self.axisChanged(3,  1)
        self.updateDisplay()
        
    def doRotationSlot(self):
        c=self.searchCrystal()
        if c and self.axisVectors[0] and self.axisVectors[1]:
            fv=self.fromVect()
            tv=self.toVect()
            if fv and tv:
                res=calcAngles(fv, tv, self.axisVectors[1], self.axisVectors[0])
                if len(res)>0:
                    for i in range(2):
                        c.addRotation(Mat3D(self.axisVectors[i], res[0][1-i]))
                    self.updateDisplay()
        

        
    def updateDisplay(self):
        c=self.searchCrystal()
        if c and self.axisVectors[0] and self.axisVectors[1]:
            fv=self.fromVect()
            tv=self.toVect()
            if fv and tv:
                res=calcAngles(fv, tv, self.axisVectors[1], self.axisVectors[0])
                if len(res)>0:
                    self.axis1Display.setText('%.2f'%math.degrees(res[0][1]))
                    self.axis2Display.setText('%.2f'%math.degrees(res[0][0]))
                else:
                    self.axis1Display.setText('-----')
                    self.axis2Display.setText('-----')
        else:
            self.axis1Display.setText('-----')
            self.axis2Display.setText('-----')

        
