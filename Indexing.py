from Tools import SolutionFinder
from PyQt4 import QtCore,  QtGui
from Ui_Indexing import Ui_Indexing
from Queue import Empty
from ToolBox import Indexer
from Tools import SpaceGroup

class Indexing(QtGui.QWidget, Ui_Indexing):
    def __init__(self, crystal, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.crystal=crystal
        self.connect(self.startButton, QtCore.SIGNAL('pressed()'), self.startIndexing)
        
        for tv in (self.SolutionDisplay, self.SolutionSelector):
            height = tv.fontMetrics().height()
            tv.verticalHeader().setDefaultSectionSize(height); 
        
        self.solutions=Indexer()
        self.SolutionSelector.setModel(self.solutions)
        self.solDisp=SolutionDisplayModel()
        self.SolutionDisplay.setModel(self.solDisp)
        self.connect(self.SolutionSelector.selectionModel (), QtCore.SIGNAL('currentRowChanged ( const QModelIndex&, const QModelIndex&)'), self.updateSolutionDisplay)
        
    def startIndexing(self):
        params=self.solutions.IndexingParameter() 
        
        V=[]
        for p in self.crystal.getConnectedProjectors():
            V+=p.getMarkerNormals()
        params.markerNormals=V
        
        V=[]
        for r in  self.crystal.getReflectionList():
            if r.Q<0.5:
                V.append(r)
        params.refs=V
        
        sg=SpaceGroup.SpaceGroup()
        sg.parseGroupSymbol(self.crystal.getSpacegroupSymbol())
        params.pointGroup=sg.getLaueGroup()
        
        params.maxAngularDeviation=self.AngDev.value()
        params.maxIntegerDeviation=self.IntDev.value()
        params.maxOrder=self.MaxIdx.value()
        params.orientationMatrix=self.crystal.getReziprocalOrientationMatrix()
        
        self.solutions.startIndexing(params)
            

    def updateSolutionDisplay(self, index, prev):
        n=index.row()
        if n>=0:
            s=self.solutions.getSolution(n)
            self.solDisp.setSolution(s)
            self.crystal.setRotation(s.bestRotation.transposed())

        
        
class SolutionDisplayModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.solution=None
        
    def rowCount(self, p):
        if self.solution==None:
            return 0
        return len(self.solution.items)
        
    def columnCount(self, p):
        return 9
        
    def setSolution(self, s):
        self.solution=s
        self.reset()
    
    def data(self, index, role):
        si=self.solution.items[index.row()]
        if role==QtCore.Qt.DisplayRole:
            if index.column() in (0, 1, 2):
                v=(si.h,  si.k,  si.l)[index.column()]
                return QtCore.QVariant('%2i'%v)
            elif index.column() in (3, 4, 5):
                v=si.rationalHkl[index.column()-3]
                return QtCore.QVariant('%.2f'%v)
            elif index.column()==6:
                return QtCore.QVariant(si.angularDeviation())
            elif index.column()==7:
                return QtCore.QVariant(si.spatialDeviation())
            elif index.column()==8:
                return QtCore.QVariant(si.hklDeviation())
        elif  role==QtCore.Qt.BackgroundRole and si.initialIndexed:
            return QtCore.QVariant(QtGui.QBrush(QtCore.Qt.green))
        return QtCore.QVariant()
