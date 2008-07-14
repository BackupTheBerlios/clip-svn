from Tools import SolutionFinder
from PyQt4 import QtCore,  QtGui
from Ui_Fit import Ui_Fit
from ToolBox import Indexer
from Tools import SpaceGroup
import math
from ToolWidget import ToolWidget

class Fit(ToolWidget, Ui_Fit, QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        ToolWidget.__init__(self, 'Fit', parent)
        QtCore.QAbstractTableModel.__init__(self)
        self.setupUi(self)
        self.model=FitModel()
        self.markerView.setModel(self.model)
        self.connect(self.indexButton, QtCore.SIGNAL('pressed()'),  self.doIndexing)
        
    def doIndexing(self):
        p=self.searchProjector()
        self.model.HKL=[]
        self.model.order=[]
        
        if p:
            N=p.projector.getMarkerNormals()
            c=p.projector.getCrystal()
            T=c.getReziprocalOrientationMatrix().inverse()
            T*=c.getRotationMatrix().transposed()
            for n in N:
                v=T*n
                v/=max([abs(x) for x in v])
                for i in range(1, 50):
                    v2=v*i
                    s=0
                    for j in range(3):
                        s+=abs(v2[j]-round(v2[j]))
                    if s<0.1:
                        break

                self.model.HKL.append([round(x) for x in v2])
                self.model.order.append(i)
                self.model.reset()
                
                
class FitModel(QtCore.QAbstractTableModel):
    def __init__(self,  parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.order=[]
        self.HKL=[]
    
    def rowCount(self, p):
        return len(self.order)
        
    def columnCount(self, p):
        return 4
            
    def data(self, index, role):
        if role==QtCore.Qt.DisplayRole:
            if index.column()==0:
                return QtCore.QVariant(self.order[index.row()])
            else:
                return QtCore.QVariant(self.HKL[index.row()][index.column()-1])
        return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        return QtCore.QVariant()

    
