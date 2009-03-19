from PyQt4 import QtCore,  QtGui
from Ui_Indexing import Ui_Indexing
from ToolBox import Indexer
from Tools import SpaceGroup
import math

class Indexing(QtGui.QWidget, Ui_Indexing):
    def __init__(self, crystal, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.crystal=crystal
        self.connect(self.startButton, QtCore.SIGNAL('pressed()'), self.startIndexing)
        
            
        self.solutions=Indexer()
        self.SolutionSelector.setModel(self.solutions)
        self.solDisp=SolutionDisplayModel()
        self.SolutionDisplay.setModel(self.solDisp)
        self.connect(self.SolutionSelector.selectionModel(), QtCore.SIGNAL('currentRowChanged ( const QModelIndex&, const QModelIndex&)'), self.updateSolutionDisplay)
        self.connect(self.solutions, QtCore.SIGNAL('runningStateChanged(bool)'), self.updateRunLabel)
        self.connect(self.stopButton, QtCore.SIGNAL('pressed()'), self.solutions,  QtCore.SIGNAL('stopWorker()'))
        
        self.connect(self.solutions, QtCore.SIGNAL('progressInfo(int,int)'), self.updateProgress)
        
        
        for tv in (self.SolutionDisplay, self.SolutionSelector):
            height = tv.fontMetrics().height()
            tv.verticalHeader().setDefaultSectionSize(height); 
        self.SolutionSelector.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.SolutionDisplay.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        for n in (6, 7, 8):
            self.SolutionDisplay.horizontalHeader().setResizeMode(n, QtGui.QHeaderView.Stretch)
            
        self.updateRunLabel(False)

    def updateRunLabel(self, b):
        if b:
            self.runLabel.setText('Running')
            self.progress.setEnabled(True)
            p=self.runLabel.palette()
            p.setColor(self.runLabel.backgroundRole(), QtGui.QColor(0x80, 0xFF, 0x80))
            self.runLabel.setPalette(p)
        else:
            self.runLabel.setText('Idle')
            self.progress.setEnabled(False)
            self.runLabel.setPalette(QtGui.QPalette())
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
        

    def startIndexing(self):
        params=self.solutions.IndexingParameter() 
        
        V=[]
        for p in self.crystal.getConnectedProjectors():
            V+=p.getMarkerNormals()
        params.markerNormals=V
        
        L=self.crystal.getReflectionList()
        L.sort(lambda x, y:cmp(x.Q, y.Q))
        params.refs=L[:min(len(L), self.numberOfTried.value())]
        
        sg=SpaceGroup.SpaceGroup()
        sg.parseGroupSymbol(self.crystal.getSpacegroupSymbol())
        params.pointGroup=sg.getLaueGroup()
        
        params.maxAngularDeviation=math.radians(self.AngDev.value())
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
            for i in s.items:
                print i.h,  i.k,  i.l,  s.bestRotation.transposed()*i.latticeVector, s.bestRotation.transposed()*i.rotatedMarker
                
    def updateProgress(self, max, act):
        self.progress.setMaximum(max)
        self.progress.setValue(act)
        #print "progress", max, act, 100.0*act/max
        
                
        
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
            return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(225, 255, 225)))
        return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Horizontal:
            data=('h', 'k', 'l', 'h', 'k', 'l', 'Angular', 'Spatial', 'HKL')
            return QtCore.QVariant(data[section])
        return QtCore.QVariant()

