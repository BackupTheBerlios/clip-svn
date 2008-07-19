from Ui_Crystal import Ui_Crystal
from PyQt4 import QtCore, QtGui
from Tools import SpaceGroup,  Icons
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
        
        self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.fileopen)), 'Open', self.slotOpenCrystalData)
        self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.filesave)), 'Save', self.slotSaveCrystalData)
        self.toolBar.addAction('Index', self.slotStartIndexing)
        
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
        

    def calcOrientation(self):
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
        return math.degrees(omega), math.degrees(chi), math.degrees(phi)

    def updateOM(self):
        omega, chi, phi=self.calcOrientation()
        self.inhibitRotationUpdate=True
        for w, p in zip(self.rotInputs,  (omega,  chi,  phi)):
            w.setValue(p)
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
        
    def slotStartIndexing(self):
        w=Indexing(self.crystal)
        mdi=self.parent().mdiArea()
        mdi.addSubWindow(w)
        w.show()

    def slotSaveCrystalData(self):
        import xml.dom.minidom
        doc=xml.dom.minidom.Document()
        crystal=doc.appendChild(doc.createElement('Crystal'))

        sg=crystal.appendChild(doc.createElement('Spacegroup'))
        sg.setAttribute('symbol', str(self.crystal.getSpacegroupSymbol()))

        cell=crystal.appendChild(doc.createElement('Cell'))
        for val, name in zip(self.crystal.getCell(), ('a', 'b', 'c', 'alpha', 'beta', 'gamma')):
            cell.setAttribute(name, str(val))

        orient=crystal.appendChild(doc.createElement('Orientation'))
        for val, name in zip(self.calcOrientation(), ('omega', 'chi','phi')):
            orient.setAttribute(name, str(val))

        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Choose File to save Cell', '', 'Clip Cell files (*.cell);;All Files (*)')
        if fileName!="":
            doc.writexml(open(fileName, 'w'), addindent='  ',newl='\n')
            
    def getAttibutes(self, doc, elementName, attibuteNames):
        element=doc.getElementsByTagName(elementName)
        if len(element)!=1:
            return
        element=element[0]
        r=[]
        for an in attibuteNames:
            s=element.getAttribute(an)
            if s=='':
                return
            r.append(s)
        return r

    def slotOpenCrystalData(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Choose Cell to load from File', '', 'Clip Cell files (*.cell);;All Files (*)'))
        try:
            import xml.dom.minidom
            doc=xml.dom.minidom.parse(fileName)
            
            sgName=self.getAttibutes(doc, 'Spacegroup', ('symbol', ))
            if sgName==None:
                return
            sgName=sgName[0]
            
            cellData=self.getAttibutes(doc, 'Cell', ('a', 'b', 'c', 'alpha', 'beta', 'gamma'))
            if cellData==None:
                return
            cellData=[float(v) for v in cellData]

            orient=self.getAttibutes(doc, 'Orientation', ('omega', 'chi','phi'))
            if orient==None:
                return
            orient=[float(v) for v in orient]

        except:
            return
        else:
            self.crystal.setSpacegroupSymbol(sgName)
            self.crystal.setCell(*cellData)
            R=Mat3D()
            for a, n in zip(orient, (2, 0, 2)):
                v=Vec3D(0, 0, 0)
                v[n]=1
                R*=Mat3D(v, math.radians(a))
            self.crystal.setRotation(R)

            
