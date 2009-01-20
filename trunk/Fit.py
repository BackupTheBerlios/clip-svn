from Tools import SolutionFinder,  SpaceGroup
from PyQt4 import QtCore,  QtGui
from Ui_Fit import Ui_Fit
from ToolBox import Vec3D, Mat3D, FitObject
from Tools import SpaceGroup
import math
from ToolWidget import ToolWidget
import scipy.optimize
from time import time


class Fit(ToolWidget, Ui_Fit, QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        ToolWidget.__init__(self, 'Fit', parent)
        QtCore.QAbstractTableModel.__init__(self)
        self.setupUi(self)
        self.HKL=[]
        self.scores=[]
        self.runParams={}

        self.paramModel=ParamModel(self)
        self.fitModel=FitModel(self)
        self.paramView.setModel(self.paramModel)
        self.markerView.setModel(self.fitModel)
        
        
        self.markerView.verticalHeader().setDefaultSectionSize(self.markerView.fontMetrics().height()) 
        #self.paramView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #self.markerView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.markerView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        for n in (6, 7):
            self.markerView.horizontalHeader().setResizeMode(n, QtGui.QHeaderView.Stretch)
        
        
        
        self.connect(self.paramModel, QtCore.SIGNAL('modelReset()'),  self.paramView.expandAll)
        
        self.connect(self.indexButton, QtCore.SIGNAL('pressed()'),  self.doIndexing)
        self.connect(self.fitButton, QtCore.SIGNAL('pressed()'),  self.doFit)

        
    def doIndexing(self):
        c=self.searchCrystal()
        self.HKL=[]
        self.scores=[]
        if c:
            for p in c.getConnectedProjectors():
                N=p.getMarkerNormals()
                T=c.getReziprocalOrientationMatrix().inverse()
                T*=c.getRotationMatrix().transposed()
                for n in N:
                    v=T*n
                    m=max([abs(x) for x in v])
                    v/=m
                    for i in range(1, 50):
                        r=v*i
                        h=Vec3D([round(x) for x in r])
                        s=(r*h)/(r*r)
                        if (r*s-h).norm()<0.1:
                            break
                    
                    self.HKL.append((r*s, h))
                    angleDiff=math.degrees(math.acos(c.hkl2Reziprocal(h).normalized()*n))
                    hklDev=sum([abs(x) for x in r*s-h])
                    self.scores.append((angleDiff, hklDev))
        self.fitModel.reset()
        
    def refineCell(self, crystal, projectors):
        last=0
        loops=0
        d=0
        K=[Vec3D(round(h), round(k), round(l)) for ((h, k, l)) in self.HKL]
        O=crystal.getReziprocalOrientationMatrix()
        while (loops<3 or abs(last-d)>1e-4):
            last=d
            loops+=1
            
            normals=[]
            for p in projectors:
                normals+=p.getMarkerNormals()
            
            N=[ x*(O*y).norm() for x,y in zip(normals,K) ]
        
            A=reduce(lambda x,y:x+y, [x^y for x,y in zip(N,K)] )
            B=reduce(lambda x,y:x+y, [x^x for x in K] )
            C=A*B.inverse()            
            O2=C.transposed()*C
            O2=O2.inverse()

            a=math.sqrt(O2[0,0])
            b=math.sqrt(O2[1,1])
            c=math.sqrt(O2[2,2])
            newCell=[a, b, c]
        
            newCell.append(math.degrees(math.acos(O2[1,2]/b/c)))
            newCell.append(math.degrees(math.acos(O2[0,2]/a/c)))
            newCell.append(math.degrees(math.acos(O2[0,1]/a/b)))
          
            origCell=crystal.getCell()
            constrain=crystal.getSpacegroupConstrains()
            paramNr=0
            for i in range(3):
                newCell[i]*=origCell[0]/newCell[0]
                
            Avg=[[], [], [], [], [], []]
            for i, c in enumerate(constrain):
                if c==0:
                    Avg[i].append(newCell[i])
                elif c<0:
                    Avg[-c-1].append(newCell[i])
                else:
                    Avg[i].append(c)
                    
            for i in range(1, 6):
                if constrain[i]==0:
                    if crystal.fitParameterEnabled(paramNr):
                        origCell[i]=sum(Avg[i])/len(Avg[i])
                    paramNr+=1
                elif constrain[i]>0:
                    origCell[i]=constrain[i]
                else:
                    origCell[i]=origCell[-constrain[i]-1]
            
            crystal.setCell(*origCell)

            O=crystal.getReziprocalOrientationMatrix()
            
            R=Mat3D((0, 0, 0, 0, 0, 0, 0, 0, 0))
            for n, k in zip(normals, K):
                k=(O*k).normalized()
                R+=n^k
        
            U, V=R.svd()
            s=U.det()*V.det()
            if s<0.0:
                R=U*Mat3D((1, 0, 0, 0, 1, 0, 0, 0, -1))*V
            else:
                R=U*V
            crystal.setRotation(R)
            D=[(n-(R*O*k).normalized()).norm() for n,k in zip(normals,K)]
            d=sum(D)
            
        #print loops, a, b, c, alpha, beta, gamma, d
        return d
        
    def score(self, x, items,  Rinit,  crystal):
        omega, phi, chi=x[:3]
        R=Mat3D(Vec3D(0, 0, 1), omega)*Mat3D(Vec3D(1, 0, 0), chi)*Mat3D(Vec3D(0, 1, 0), phi)*Rinit
        crystal.setRotation(R)
        for v, (p, n) in zip(x[3:], items):
            p.fitParameterSetValue(n, v)

        normals=[]
        for p in crystal.getConnectedProjectors():
            normals+=p.getMarkerNormals()

        return sum([(crystal.hkl2Reziprocal(hkl).normalized()-n).norm() for (hklf, hkl), n in zip(self.HKL,  normals)])
        
    def printScore(self, x):
        print x

    def doFit(self):
        crystal=self.searchCrystal()
        
        if not crystal:
            return 
            
        self.doIndexing()
        fitItems=[]
        initialValues=[0.0, 0.0, 0.0]
        
        crystal.enableUpdate(False)
        for n in range(crystal.fitParameterNumber()):
            if crystal.fitParameterEnabled(n):
                fitItems.append((crystal,  n))
                initialValues.append(crystal.fitParameterValue(n))
                
        for p in crystal.getConnectedProjectors():
            p.enableProjection(False)
            if p.fitParameterNumber()>0 and p.markerNumber()>0:
                for n in range(p.fitParameterNumber()):
                    if p.fitParameterEnabled(n):
                        fitItems.append((p,  n))
                        initialValues.append(p.fitParameterValue(n))
        
        #res=scipy.optimize.fmin_l_bfgs_b(self.score, initialValues,  args=(crystal, projectors, fitItems), approx_grad=True)
        RInit=Mat3D(crystal.getRotationMatrix())
        res=scipy.optimize.fmin(self.score, initialValues,  args=(fitItems,  RInit, crystal), callback=self.printScore)
            
        print res
        print self.score(res, fitItems,  RInit, crystal)
        crystal.enableUpdate(True)
        crystal.updateRotation()
        for p in crystal.getConnectedProjectors():
            p.enableProjection(True)
            p.reflectionsUpdated()
        
        self.doIndexing()
        self.paramModel.reset()
        self.fitModel.reset()

    def windowChanged(self):
        self.paramModel.loadModel()
    
    def crystalConstrainChanged(self):
        self.paramModel.loadModel()
        self.paramModel.reset()
                
class FitModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.fit=parent
        
    def rowCount(self, p):
        return len(self.fit.HKL)
        
    def columnCount(self, p):
        return 8
            
    def data(self, index, role):
        if role==QtCore.Qt.DisplayRole:
            c=index.column()
            if c<3:
                return QtCore.QVariant(round(self.fit.HKL[index.row()][0][index.column()]))
            elif c<6:
                return QtCore.QVariant('%.2f'%self.fit.HKL[index.row()][0][index.column()-3])
            else:
                return QtCore.QVariant('%.3f'%self.fit.scores[index.row()][index.column()-6])
        elif role==QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignRight)
        return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Horizontal:
            data=('h', 'k', 'l', 'h', 'k', 'l', 'Angular',  'HKL')
            return QtCore.QVariant(data[section])
        return QtCore.QVariant()
        return QtCore.QVariant()        

class ParamModel(QtCore.QAbstractItemModel):
    def __init__(self, parent):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.fit=parent
        self.rootItems=[]
        self.names=[]
        self.lastCrystal=None
        
    def loadModel(self):
        c=self.fit.searchCrystal()
        if not c:
            return
        
        rootItems=[]
        names=[]
        if c.fitParameterNumber()>0:
            rootItems.append(c)
            names.append('Cell')
            
        for p in c.getConnectedProjectors():
            if p.fitParameterNumber()>0 and p.markerNumber()>0:
                rootItems.append(p)
                names.append(p.configName())
                
        if rootItems!=self.rootItems:
            self.rootItems=rootItems
            self.names=names
            self.lastCrystal=c
            self.reset()
        
    def rowCount(self, parent):
        if not parent.isValid():
            # Toplevel == Crystal + projectors
            return len(self.rootItems)
        elif parent.internalId()<0:
            return self.rootItems[parent.row()].fitParameterNumber()
        return 0
        

    def columnCount(self, parent):
        return 2

    def index(self, row, column, parent):
        if parent.isValid():
            return self.createIndex(row, column, parent.row())
        else:
            return self.createIndex(row, column, -1)
        
    def parent(self, index):
        if index.internalId()<0:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(index.internalId(), 0, -1)
        
        
    def data(self, index, role):
        if role==QtCore.Qt.DisplayRole:
            if index.internalId()<0 and index.column()==0:
                return QtCore.QVariant(self.names[index.row()])
            elif index.internalId()>=0:
                if index.column()==0:
                    return QtCore.QVariant(self.rootItems[index.internalId()].fitParameterName(index.row()))
                elif index.column()==1:
                    return QtCore.QVariant(self.rootItems[index.internalId()].fitParameterValue(index.row()))
        elif role==QtCore.Qt.CheckStateRole and index.internalId()>=0 and index.column()==0:
            t = self.rootItems[index.internalId()].fitParameterEnabled(index.row())
            if t:
                return QtCore.QVariant(QtCore.Qt.Checked)
            else:
                return QtCore.QVariant(QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def flags(self, index):
        if index.internalId()>=0 and index.column()==0:
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled
            
    def setData(self, index, value, role):
        if role==QtCore.Qt.CheckStateRole and index.internalId()>=0:
            self.rootItems[index.internalId()].fitParameterSetEnabled(index.row(), value.toBool())
            id1=self.index(0,  index.column(), index.parent())
            id2=self.index(self.rowCount(index.parent()),  index.column(), index.parent())
            self.emit(QtCore.SIGNAL('dataChanged(const QModelIndex&, const QModelIndex&)'), id1, id2)
            return True
        return False
            
    def headerData(self, section, orientation, role):
        return QtCore.QVariant()
    

    

