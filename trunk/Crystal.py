from Ui_Crystal import Ui_Crystal
from PyQt4 import QtCore, QtGui
from Tools import SpaceGroup, getXMLAttributes
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
        
        self.crystal=ToolBox.Crystal(self)

        self.connect(self.SpaceGroup, QtCore.SIGNAL("textChanged(const QString &)"), self.sgtest)
        
        for w in self.inputs:
            self.connect(w, QtCore.SIGNAL("valueChanged(double)"), self.publish)
    
        for w in self.rotInputs:
            self.connect(w, QtCore.SIGNAL("valueChanged(double)"), self.changeRotation)
        
        self.connect(self.crystal,  QtCore.SIGNAL('orientationChanged()'),  self.updateOM)
        self.connect(self.crystal,  QtCore.SIGNAL('cellChanged()'),  self.updateOM)
        self.connect(self.crystal,  QtCore.SIGNAL('cellChanged()'),  self.loadCellFromCrystal)
        
        self.toolBar.addAction(QtGui.QIcon(':/fileopen.png'), 'Open', self.slotOpenCrystalData)
        self.toolBar.addAction(QtGui.QIcon(':/filesave.png'), 'Save', self.slotSaveCrystalData)
        self.toolBar.addAction(QtGui.QIcon(':/Index.png'),'Index', self.slotStartIndexing)
        
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
            
            sgold=SpaceGroup.SpaceGroup()
            sgold.parseGroupSymbol(self.crystal.getSpacegroupSymbol())
            self.crystal.setSpacegroupSymbol(s)
            
            if self.sg.system==self.sg.trigonal:
                self.crystal.setSpacegroupConstrains([0,0,0,0,0,0])
                if sgold.getCellConstrain()==[0,-1,-1,0,-4,-4] and self.sg.getCellConstrain()==[0,-1,0,90,90,120]:
                    self.R2T(self.crystal)
                elif sgold.getCellConstrain()==[0,-1,0,90,90,120] and self.sg.getCellConstrain()==[0,-1,-1,0,-4,-4]:
                    self.T2R(self.crystal)

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
        angs=self.crystal.calcEulerAngles()
        self.inhibitRotationUpdate=True
        for w, p in zip(self.rotInputs,  angs):
            w.setValue(math.degrees(p))
        for i in range(3):
            for j in range(3):
                self.orientationMatrix.setItem(i, j, QtGui.QTableWidgetItem('%.4f'%OM[i, j]))            
        self.inhibitRotationUpdate=False
        
    def changeRotation(self):
        if not self.inhibitRotationUpdate:
            angs=[math.radians(x.value()) for x in self.rotInputs]
            self.crystal.setEulerAngles(*angs)
                    
    def mousePressEvent(self,  e):
        if e.button()==QtCore.Qt.LeftButton and self.dragStart.geometry().contains(e.pos()):
            self.mousePressStart=QtCore.QPoint(e.pos())
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

    def crystaldata2xml(self, w):                
        w.writeStartElement('Crystal')
        
        w.writeEmptyElement('Spacegroup')
        w.writeAttribute('symbol', str(self.crystal.getSpacegroupSymbol()))
        
        w.writeEmptyElement('Cell')
        for val, name in zip(self.crystal.getCell(), ('a', 'b', 'c', 'alpha', 'beta', 'gamma')):
            w.writeAttribute(name, str(val))
            
        w.writeEmptyElement('Orientation')
        for val, name in zip(self.crystal.calcEulerAngles()[:3], ('omega', 'chi','phi')):
            w.writeAttribute(name, str(math.degrees(val)))
        
        w.writeEndElement()

    def loadFromXML(self, r):
        if r.name()!="Crystal" or not r.isStartElement():
            return
        while not r.atEnd() and not (r.isEndElement() and r.name()=="Crystal"):
            if r.readNext()==QtCore.QXmlStreamReader.StartElement:
                if r.name()=="Spacegroup":
                    s=r.attributes().value('symbol')
                    if not s.isNull():
                        self.crystal.setSpacegroupSymbol(str(s.toString()))
                elif r.name()=="Cell":
                    cell=[]
                    for name in ('a', 'b', 'c', 'alpha', 'beta', 'gamma'):
                        s=r.attributes().value(name)
                        v, b=s.toString().toDouble()
                        if not s.isNull() and b:
                            cell.append(v)
                    if len(cell)==6:
                        self.crystal.setCell(*cell)
                elif r.name()=="Orientation":
                    angles=[]
                    for name in ('omega', 'chi', 'phi'):
                        s=r.attributes().value(name)
                        v, b=s.toString().toDouble()
                        if not s.isNull() and b:
                            angles.append(math.radians(v))
                    if len(angles)==3:
                        self.crystal.setEulerAngles(*angles)
        
    def slotSaveCrystalData(self):
        xmlString=QtCore.QString()
        w=QtCore.QXmlStreamWriter(xmlString)
        w.setAutoFormatting(True)
        w.setAutoFormattingIndent(2)

        self.crystaldata2xml(w)
        w.writeEndDocument()
        print xmlString
        
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Choose File to save Cell', '', 'Clip Cell files (*.cell);;All Files (*)')
        if fileName!="":
            f=open(str(fileName),  'w')
            f.write(str(xmlString))
            f.close()
            

    def slotOpenCrystalData(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Choose Cell to load from File', '', 'Clip Cell files (*.cell);;All Files (*)'))
        try:
            f=open(str(fileName))
            s=''.join(f.readlines())
        except:
            return
        else:
            r=QtCore.QXmlStreamReader(s)
            while not r.atEnd():
                r.readNext()
                if r.name()=='Crystal' and r.isStartElement():
                    self.loadFromXML(r)
                    
    def R2T(self, Cr):
        a,b,c,al,be,ga=Cr.getCell()
        if a==b and b==c and al==be and be==ga:
            a=Cr.uvw2Real(1,-1,0)
            c=Cr.uvw2Real(1,1,1)
            Cr.setCell(a.norm(),a.norm(),c.norm(),90,90,120)
            ch=Cr.uvw2Real(0,0,1)
            Cr.addRotation(self.rotHT(a,c,Cr.uvw2Real(1,0,0),Cr.uvw2Real(0,0,1),-1))
  
    def T2R(self, Cr):
        a,b,c,al,be,ga=Cr.getCell()
        if a==b and al==90.0 and be==90.0 and ga==120.0:
            a=Cr.uvw2Real(2,1,1)/3
            b=Cr.uvw2Real(-1,1,1)/3
            ah=Cr.uvw2Real(1,0,0)
            ch=Cr.uvw2Real(0,0,1)
            l=a.norm()
            ang=math.degrees(math.acos(a*b/l/l))
            Cr.setCell(l,l,l,ang,ang,ang)
            Cr.addRotation(self.rotHT(Cr.uvw2Real(1,-1,0),Cr.uvw2Real(1,1,1),ah,ch,1))


    def rotHT(self,r1,r2,ah,ch,o):

        da=r1-ah
        dc=r2-ch
        
        n=da%dc
        n.normalize()

        c1=r2-n*(n*r2)
        c2=ch-n*(ch*n)
        c1.normalize()
        c2.normalize()
        R=Mat3D(n,o*math.acos(c1*c2))
        return R
