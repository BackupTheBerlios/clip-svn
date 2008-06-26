from Ui_CrystalWidget import Ui_CrystalWidget
from PyQt4 import QtCore, QtGui
from Tools import SpaceGroup
import ToolBox
from ToolBox import Vec3D,  Mat3D
import math
from Indexing import Indexing

class Crystal(QtGui.QWidget, Ui_CrystalWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.orientationMatrix.horizontalHeader().hide()
        self.orientationMatrix.verticalHeader().hide()

        self.valid=False
        self.cell = []
        self.sgName=None
        self.sg=SpaceGroup.SpaceGroup()
        self.inputs=(self.latticeA, self.latticeB, self.latticeC, self.latticeAlpha, self.latticeBeta, self.latticeGamma)
        
        self.rotInputs=(self.rotationOmega,  self.rotationChi,  self.rotationPhi)

        
        self.crystal=ToolBox.Crystal()
    
        validators = ((self.latticeA,     0.1, 1000.0,  4),
                            (self.latticeB,     0.1, 1000.0,  4),
                            (self.latticeC,     0.1, 1000.0,  4),
                            (self.latticeAlpha, 0.01, 179.99, 3),
                            (self.latticeBeta,  0.01, 179.99, 3),
                            (self.latticeGamma, 0.01, 179.99, 3))
                            
    
        for  w,  lower,  upper,  digits in validators:
            w.setValidator(QtGui.QDoubleValidator(lower,  upper, digits,  w))
            
            self.connect(w, QtCore.SIGNAL("editingFinished()"), self.publish)
            self.connect(w, QtCore.SIGNAL("returnPressed()"), self.nextFocus)
            self.connect(w, QtCore.SIGNAL("textChanged(const QString &)"), self.symConstrain)
    
        self.connect(self.SpaceGroup, QtCore.SIGNAL("textChanged(const QString &)"), self.sgtest)
        self.connect(self.SpaceGroup, QtCore.SIGNAL("editingFinished()"), self.publish)
        self.connect(self.SpaceGroup, QtCore.SIGNAL("returnPressed()"), self.nextFocus)
        
        for w in self.rotInputs:
            w.setValidator(QtGui.QDoubleValidator(-360.0,  360.0,  2,  w))
            self.connect(w, QtCore.SIGNAL("editingFinished()"), self.changeRotation)
        
        self.connect(self.crystal,  QtCore.SIGNAL('orientationChanged()'),  self.updateOM)
        self.connect(self.crystal,  QtCore.SIGNAL('cellChanged()'),  self.updateOM)
        
        ac1=self.toolBar.addAction('Load')
        ac1=self.toolBar.addAction('Save')
        ac1=self.toolBar.addAction('Index')
        self.connect(ac1,  QtCore.SIGNAL('triggered()'),  self.startIndexing)

    def sizeHint(self):
        return self.minimumSizeHint()

    def resizeEvent(self, e):
        w=self.orientationMatrix.width()/3
        h=self.orientationMatrix.height()/3
        for i in range(3):
            self.orientationMatrix.setColumnWidth(i, w)
            self.orientationMatrix.setRowHeight(i, h)


    def setCell(self, cell):
        for inp, val in zip(self.inputs, cell):
            d=inp.validator().decimals()
            inp.setText(QtCore.QString("%1").arg(float(val), 0, 'f', d))
        self.publish()

    def publish(self):
        if self.valid:
            self.emit(QtCore.SIGNAL("structurChanged"), self.sgName, self.cell)
            self.crystal.setCell(*self.cell)
        else:
            self.topLevelWidget().statusBar().showMessage("Lattice parameter or space group symbol not valid", 2000)

    def symConstrain(self):
        self.valid=(self.sgName!=None)
        cell=[]
        symConst=self.sg.getCellConstrain()
        for i in range(6):
            self.valid=self.valid and self.inputs[i].hasAcceptableInput()
            self.inputs[i].setEnabled(symConst[i]==0)
            cell.append(self.inputs[i].text().toDouble()[0])
        self.cell=self.sg.contrainCellToSymmetry(cell)
        for i in range(6):
            if symConst[i]!=0:
                self.inputs[i].setText(str(self.cell[i]))

    def sgtest(self, s):
        if self.sg.parseGroupSymbol(str(s)):
            self.sgName=str(s)
            self.crystal.setSpacegroupSymbol(s)
        else:
            self.sgName=None
        self.symConstrain()

    def wheelEvent(self, e):
        for i in self.inputs+self.rotInputs:
            if i.isEnabled and i.underMouse():
                d=i.validator().decimals()
                if e.modifiers()&QtCore.Qt.ShiftModifier:
                    d-=2
                if e.modifiers()&QtCore.Qt.ControlModifier:
                    d-=1
                v=i.text().toDouble()[0]+10.0**(1.0-d)*e.delta()/120.0
                t=QtCore.QString("%%0.%sf" %d %v)
                pos=0
                if i.validator().validate(t,pos)[0]==QtGui.QValidator.Acceptable:
                    i.selectAll()
                    i.insert(t)
                    if i in self.inputs:
                        self.publish()
                    elif i in self.rotInputs:
                        self.changeRotation()
                
    def nextFocus(self):
        self.focusNextPrevChild(True)
        
    def updateOM(self):
        OM=self.crystal.getReziprocalOrientationMatrix()
        R=self.crystal.getRotationMatrix()
        OM=R*OM
        for i in range(3):
            for j in range(3):
                self.orientationMatrix.setItem(i, j, QtGui.QTableWidgetItem('%.4f'%OM[i, j]))
        v=R*Vec3D(0, 0, 1)
        omega=math.atan2(v.x(), -v.y())
        Rom=Mat3D(Vec3D(0, 0, 1),  -omega)
        v=Rom*v
        chi=math.atan2(-v.y(), v.z())
        Rchi=Mat3D(Vec3D(1, 0, 0),  -chi)
        Rphi=Rchi*Rom*R
        v=Rphi*Vec3D(1, 0, 0)
        phi=math.atan2(v.y(),  v.x())
        #print 'Winkel:',  math.degrees(omega),  math.degrees(chi),  math.degrees(phi)
        for w, p in zip(self.rotInputs,  (omega,  chi,  phi)):
            w.setText('%.3f'%math.degrees(p))
        
    def changeRotation(self):
        OM=Mat3D()
        for w, p in zip(self.rotInputs,  (2, 0,2)):
            try:
                ang=float(w.text())
            except:
                return
            ax=Vec3D(0, 0, 0)
            ax[p]=1.0
            OM=OM*Mat3D(ax,  math.radians(ang))
        self.crystal.setRotation(OM)
        
    def mousePressEvent(self,  e):
        if e.button()==QtCore.Qt.LeftButton and self.dragStart.geometry().contains(e.pos()):
            self.mousePressStart=QtCore.QPoint(e.pos())
            print 'Possibly start Drag', e.pos().x(),  e.pos().y()
            drag=QtGui.QDrag(self)
            mimeData=QtCore.QMimeData()
            mimeData.setData('application/CrystalPointer','')
            drag.setMimeData(mimeData)
            res=drag.exec_(QtCore.Qt.LinkAction) 
            
    def mouseMoveEvent(self,  e):
        p=self.mousePressStart
        dragLen=(e.pos()-p).manhattanLength()
        if (e.buttons()==QtCore.Qt.LeftButton) and (dragLen>QtGui.QApplication.startDragDistance()) and (self.dragStart.geometry().contains(p)):
            pass

        
    def mouseReleaseEvent(self,  e):
        pass
        
    def startIndexing(self):
        w=Indexing(self.crystal)
        mdi=self.parent().mdiArea()
        mdi.addSubWindow(w)
        w.show()
        
