from Ui_Crystal import Ui_Crystal
from PyQt4 import QtCore, QtGui
from Tools import SpaceGroup
import ToolBox
from ToolBox import Vec3D,  Mat3D
import math
from Indexing import Indexing

class Crystal(QtGui.QWidget, Ui_Crystal):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.orientationMatrix.horizontalHeader().hide()
        self.orientationMatrix.verticalHeader().hide()

        self.inhibitRotationUpdate=True

        self.sg=SpaceGroup.SpaceGroup()
        self.inputs=(self.latticeA, self.latticeB, self.latticeC, self.latticeAlpha, self.latticeBeta, self.latticeGamma)
        self.rotInputs=(self.rotationOmega,  self.rotationChi,  self.rotationPhi)
        
        self.crystal=ToolBox.Crystal()

        self.connect(self.SpaceGroup, QtCore.SIGNAL("textChanged(const QString &)"), self.sgtest)
        
        for w in self.inputs:
            self.connect(w, QtCore.SIGNAL("valueChanged(double)"), self.publish)
    
        for w in self.rotInputs:
            self.connect(w, QtCore.SIGNAL("valueChanged(double)"), self.changeRotation)
        
        self.connect(self.crystal,  QtCore.SIGNAL('orientationChanged()'),  self.updateOM)
        self.connect(self.crystal,  QtCore.SIGNAL('cellChanged()'),  self.updateOM)
        self.connect(self.crystal,  QtCore.SIGNAL('cellChanged()'),  self.loadCellFromCrystal)
        
        ac1=self.toolBar.addAction('Load')
        ac1=self.toolBar.addAction('Save')
        ac1=self.toolBar.addAction('Index')
        self.connect(ac1,  QtCore.SIGNAL('triggered()'),  self.startIndexing)
        
        self.loadCellFromCrystal()

    def sizeHint(self):
        return self.minimumSizeHint()

    def resizeEvent(self, e):
        w=self.orientationMatrix.width()/3
        h=self.orientationMatrix.height()/3
        for i in range(3):
            self.orientationMatrix.setColumnWidth(i, w)
            self.orientationMatrix.setRowHeight(i, h)

    def loadCellFromCrystal(self):
        self.SpaceGroup.setText(self.crystal.getSpacegroupSymbol())
        cell=self.crystal.getCell()
        for val, inp in zip(cell, self.inputs):
            inp.setValue(val)

    def publish(self):
        cell=self.sg.contrainCellToSymmetry([w.value() for w in self.inputs])
        self.crystal.setCell(*cell)

    def sgtest(self, s):
        if self.sg.parseGroupSymbol(str(s)):
            self.crystal.setSpacegroupSymbol(s)
            self.crystal.setSpacegroupConstrains(self.sg.getCellConstrain())
    
        constrain=self.sg.getCellConstrain()
        for i in range(6):
            self.inputs[i].setEnabled(constrain[i]==0)
        cell=self.sg.contrainCellToSymmetry(self.crystal.getCell())
        self.crystal.setCell(*cell)
        

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
        self.inhibitRotationUpdate=True
        for w, p in zip(self.rotInputs,  (omega,  chi,  phi)):
            w.setValue(math.degrees(p))
        self.inhibitRotationUpdate=False
        
    def changeRotation(self):
        if not self.inhibitRotationUpdate:
            OM=Mat3D()
            for w, p in zip(self.rotInputs,  (2, 0, 2)):
                ang=w.value()
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
        
    def startIndexing(self):
        w=Indexing(self.crystal)
        mdi=self.parent().mdiArea()
        mdi.addSubWindow(w)
        w.show()
        
