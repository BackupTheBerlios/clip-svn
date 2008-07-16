from Tools import SolutionFinder,  SpaceGroup
from PyQt4 import QtCore,  QtGui
from Ui_Fit import Ui_Fit
from ToolBox import Vec3D, Mat3D
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
        self.order=[]
        self.runParams={}

        self.paramModel=ParamModel(self)
        self.fitModel=FitModel(self)
        self.paramView.setModel(self.paramModel)
        self.markerView.setModel(self.fitModel)
        
        for tv in (self.markerView, ):
            height = tv.fontMetrics().height()
            tv.verticalHeader().setDefaultSectionSize(height); 
        #self.paramView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #self.markerView.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.markerView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        self.connect(self.paramModel, QtCore.SIGNAL('modelReset()'),  self.paramView.expandAll)
        
        self.connect(self.indexButton, QtCore.SIGNAL('pressed()'),  self.doIndexing)
        self.connect(self.fitButton, QtCore.SIGNAL('pressed()'),  self.doFit)

        
    def doIndexing(self):
        c=self.searchCrystal()
        self.HKL=[]
        self.order=[]
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
    
                    self.HKL.append(r*s)
                    self.order.append(s*i)
        self.fitModel.reset()
        
    def refineCell(self, crystal, projectors):
        last=0
        loops=0
        d=0
        K=[Vec3D(round(h), round(k), round(l)) for (h, k, l) in self.HKL]
        O=crystal.getReziprocalOrientationMatrix()
        while (loops<5 or abs(last-d)>1e-4):
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
            
            a=1.0/math.sqrt(O2[0,0])
            b=1.0/math.sqrt(O2[1,1])
            c=1.0/math.sqrt(O2[2,2])
        
            alpha=180-math.degrees(math.acos(O2[1,2]*b*c))
            beta= 180-math.degrees(math.acos(O2[0,2]*a*c))
            gamma=180-math.degrees(math.acos(O2[0,1]*a*b))
          
        
            #self.cr.setCell(a*s,b*s,c*s,alpha,beta,gamma)

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
        
    def score(self, x, crystal, projectors, items):
        t1=time()
        for v, (p, n) in zip(x, items):
            p.fitParameterSetValue(n, v)
        t2=time()
        r=self.refineCell(crystal,  projectors) 
        t3=time()
        print t2-t1, t3-t2
        return r

    def doFit(self):
        crystal=self.searchCrystal()
        
        if not crystal:
            return 
            
        self.doIndexing()
        fitItems=[]
        initialValues=[]
        projectors=[]
        crystal.enableUpdate(False)
        for p in crystal.getConnectedProjectors():
            p.enableProjection(False)
            if p.fitParameterNumber()>0 and p.markerNumber()>0:
                projectors.append(p)
                for n in range(p.fitParameterNumber()):
                    if p.fitParameterEnabled(n):
                        fitItems.append((p,  n))
                        initialValues.append(p.fitParameterValue(n))
        if len(fitItems)>0:
            res=scipy.optimize.fmin_l_bfgs_b(self.score, initialValues,  args=(crystal, projectors, fitItems), approx_grad=True, epsilon=0.001)
            print res
                
        crystal.enableUpdate(True)
        crystal.updateRotation()
        for p in crystal.getConnectedProjectors():
            p.enableProjection(True)
            p.reflectionsUpdated()

    def windowChanged(self):
        self.paramModel.loadModel()
                
                
class FitModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.fit=parent
        
    def rowCount(self, p):
        return len(self.fit.order)
        
    def columnCount(self, p):
        return 7
            
    def data(self, index, role):
        if role==QtCore.Qt.DisplayRole:
            c=index.column()
            if c==0:
                return QtCore.QVariant(self.fit.order[index.row()])
            elif c<4:
                return QtCore.QVariant(self.fit.HKL[index.row()][index.column()-1])
            elif c<7:
                return QtCore.QVariant(round(self.fit.HKL[index.row()][index.column()-4]))
        return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        return QtCore.QVariant()


class CrystalFitParams:
    def __init__(self, crystal):
        self.crystal=crystal
        self.sg=SpaceGroup.SpaceGroup()
        self.loadData()
        self.enabled=[True]*5
        
    def loadData(self):
        self.parsedSG=self.sg.parseGroupSymbol(self.crystal.getSpacegroupSymbol())
        
        
    def mayRun(self):
        constrain=self.sg.getCellConstrain()
        return [c==0 for c in constrain[1:]]
        
    
    def fitParameterNumber(self):
        constrain=self.sg.getCellConstrain()
        return sum(self.mayRun())
        
    def fitParameterName(self, i):
        names=[n for n, b in zip(('b', 'c', 'alpha', 'beta', 'gamma'), self.mayRun()) if b]
        return names[i]
        
    def fitParameterValue(self, i):
        return 6
        
    def fitParameterEnabled(self, i):
        number=[n for n, b in zip(range(5), self.mayRun()) if b]
        return self.enabled[number[i]]
        
    def fitParameterSetEnabled(self, i, b):
        number=[n for n, b in zip(range(5), self.mayRun()) if b]
        self.enabled[number[i]]=b

    def fitParameterSetValue(self, i, v):
        pass
        
    def configName(self):
        return 'Cell'
        

class ParamModel(QtCore.QAbstractItemModel):
    def __init__(self, parent):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.fit=parent
        self.rootItems=[]
        self.lastCrystal=None
        
    def loadModel(self):
        c=self.fit.searchCrystal()
        if not c:
            return
    
        rootItems=[]
        if c==self.lastCrystal and len(self.rootItems)>0 and self.rootItems[0].configName()=='Cell':
            cfp=self.rootItems[0]
            cfp.loadData()
        else:
            cfp=CrystalFitParams(c)
            
        if cfp.fitParameterNumber()>0:
            rootItems.append(cfp)

        for p in c.getConnectedProjectors():
            if p.fitParameterNumber()>0 and p.markerNumber()>0:
                rootItems.append(p)
                
        if rootItems!=self.rootItems:
            self.rootItems=rootItems
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
                return QtCore.QVariant(self.rootItems[index.row()].configName())
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
        if index.internalId()>=0 and index.column()==2:
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled
            
    def setData(self, index, value, role):
        if role==QtCore.Qt.CheckStateRole and index.internalId()>=0:
            self.rootItems[index.internalId()].fitParameterSetEnabled(index.row(), value.toBool())
            self.emit(QtCore.SIGNAL('dataChanged()'))
            return True
        return False
            
    def headerData(self, section, orientation, role):
        return QtCore.QVariant()
    

    
