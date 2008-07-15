from Tools import SolutionFinder
from PyQt4 import QtCore,  QtGui
from Ui_Fit import Ui_Fit
from ToolBox import Vec3D, Mat3D
from Tools import SpaceGroup
import math
from ToolWidget import ToolWidget

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
        
        self.connect(self.indexButton, QtCore.SIGNAL('pressed()'),  self.doIndexing)
        self.connect(self.fitButton, QtCore.SIGNAL('pressed()'),  self.doFit)

        
    def doIndexing(self):
        p=self.searchProjector()
        self.HKL=[]
        self.order=[]
        if p:
            N=p.projector.getMarkerNormals()
            c=p.projector.getCrystal()
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
                
    def doFit(self):
        pass
        
    def windowChanged(self):
        self.paramModel.reset()
                
                
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



class ParamModel(QtCore.QAbstractItemModel):
    def __init__(self, parent):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.fit=parent
        
    def rowCount(self, parent):
        c=self.fit.searchCrystal()
        if not c:
            return 0
        p=c.getConnectedProjectors()
        if not parent.isValid():
            # Toplevel == Crystal + projectors
            return len(p)
        elif parent.internalId()<0:
            return p[parent.row()].fitParameterNumber()
        return 0
                   
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
        
    def columnCount(self, parent):
        return 3
        
    def data(self, index, role):
        c=self.fit.searchCrystal()
        if not c:
            return QtCore.QVariant()
        p=c.getConnectedProjectors()
        if role==QtCore.Qt.DisplayRole:
            if index.internalId()<0 and index.column()==0:
                return QtCore.QVariant(p[index.row()].configName())
            elif index.internalId()>=0:
                if index.column()==0:
                    return QtCore.QVariant(p[index.internalId()].fitParameterName(index.row()))
                elif index.column()==1:
                    return QtCore.QVariant(p[index.internalId()].fitParameterValue(index.row()))
        elif role==QtCore.Qt.CheckStateRole and index.internalId()>=0 and index.column()==2:
            t = p[index.internalId()].fitParameterEnabled(index.row())
            if t:
                return QtCore.QVariant(QtCore.Qt.Checked)
            else:
                return QtCore.QVariant(QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def flags(self, index):
        if index.column()==0:
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled
            
    def setData(self, index, value, role):
        if role==QtCore.Qt.CheckStateRole:
            p=self.fit.searchProjector()
            if p:
                self.fit.runParams[p][index.row()]=value.toBool()
                self.emit(QtCore.SIGNAL('dataChanged()'))
                return True
        return False
            
    def headerData(self, section, orientation, role):
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Vertical:
            p=self.fit.searchProjector()
            if p:
                return QtCore.QVariant(p.projector.fitParameterName(section))
        return QtCore.QVariant()
    

    
