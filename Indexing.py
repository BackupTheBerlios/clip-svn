from Tools import SolutionFinder
from PyQt4 import QtCore,  QtGui
from Ui_Indexing import Ui_Indexing
from Tools import SolutionFinder
from Queue import Empty
class Indexing(QtGui.QWidget, Ui_Indexing):
    def __init__(self, crystal, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.sf=SolutionFinder.SolutionFinder()
        self.crystal=crystal
        self.connect(self.startButton, QtCore.SIGNAL('pressed()'), self.startIndexing)
        
        for tv in (self.SolutionDisplay, self.SolutionSelector):
            height = tv.fontMetrics().height()
            tv.verticalHeader().setDefaultSectionSize(height); 
        
        self.solutions=SolutionArrayModel()
        self.SolutionSelector.setModel(self.solutions)
        self.solDisp=SolutionDisplayModel()
        self.SolutionDisplay.setModel(self.solDisp)
        self.connect(self.SolutionSelector, QtCore.SIGNAL('clicked(const QModelIndex &)'), self.updateSolutionDisplay)
    def startIndexing(self):
        V=[]
        for p in self.crystal.getConnectedProjectors():
            V+=p.getMarkerNormals()
        print V
        self.sf.setOMat(self.crystal.getReziprocalOrientationMatrix())
        self.sf.setVectors(V)
        self.sf.setMaxAngularDeviation(self.AngDev.value())
        self.sf.setMaxDeviationFromInt(self.IntDev.value())
        self.sf.setMaxTriedIndex(self.MaxIdx.value())
        self.sf.startWork()
        self.solutions.clearSolutions()
        self.pollSolutionFinder()
        
    def pollSolutionFinder(self):
        print "Poll"
        ok=True
        grown=False
        while ok:
            try:
                s=self.sf.solutionQueue.get_nowait()
            except Empty:
                ok=False
            else:
                self.sf.solutionQueue.task_done()
                self.solutions.addSolution(s)
                grown=True


        if not self.sf.workQueue.empty() and not self.sf.solutionQueue.empty():
            QtCore.QTimer.singleShot(500, self.pollSolutionFinder)
            

    def updateSolutionDisplay(self, index):
        sol=self.solutions.store[index.row()]
        self.solDisp.setSolution(sol)
        self.crystal.setRotation(sol.bestRotation.inverse())

class SolutionArrayModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.store=[]
        
    def rowCount(self, p):
        return len(self.store)
        
    def columnCount(self, p):
        return 2
        
    def addSolution(self, s):
        self.store.append(s)
        self.reset()
        
    def clearSolutions(self):
        self.store=[]
        self.reset()
        
    def data(self, index, role):
        if index.isValid() and role==QtCore.Qt.DisplayRole:
            if index.row()<len(self.store):
                if index.column()==0:
                    return QtCore.QVariant(self.store[index.row()].solutionScore())
                elif index.column()==1:
                    return QtCore.QVariant(self.store[index.row()].angularDeviation())
        return QtCore.QVariant()
     
    def sort(self, col, order):
        if col==0:
            field=lambda x:x.solutionScore()
        else:
            field=lambda x:x.angularDeviation()
        if order==QtCore.Qt.AscendingOrder:
            self.store.sort(lambda x, y:cmp(field(x), field(y)))
        else:
            self.store.sort(lambda x, y:-cmp(field(x), field(y)))
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
        
class SolutionDisplayModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.solution=None
        
    def rowCount(self, p):
        if self.solution==None:
            return 0
        return len(self.solution.alphas)
        
    def columnCount(self, p):
        return 4
        
    def setSolution(self, s):
        self.solution=s
        self.reset()
    
        
    def data(self, index, role):
        if index.isValid() and role==QtCore.Qt.DisplayRole:
            if index.row()<self.rowCount(None):
                if index.column()==0:
                    h, k, l=self.solution.HKLs[index.row()]
                    return QtCore.QVariant('%i %i %i'%(h, k, l))
                elif index.column()==1:
                    v=self.solution.calcFractionalHKL(index.row())
                    return QtCore.QVariant('%.2f %.2f %.2f'%v)
                elif index.column()==2:
                    return QtCore.QVariant(self.solution.calcSolutionScore(index.row()))
                elif index.column()==3:
                    return QtCore.QVariant(self.solution.calcAngularDeviation(index.row()))
                
                
                
                    
        return QtCore.QVariant()
