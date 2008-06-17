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
        self.solutions=[]
        
    def startIndexing(self):
        V=[]
        for p in self.crystal.getConnectedProjectors():
            V+=p.getMarkerNormals()
        print V
        self.sf.setOMat(self.crystal.getReziprocalOrientationMatrix())
        self.sf.setVectors(V)
        self.sf.setMaxAngularDeviation(1.5)
        self.sf.setMaxDeviationFromInt(0.3)
        self.sf.setMaxTriedIndex(3)
        self.sf.startWork()
        self.solutions=[]
        self.pollSolutionFinder()
        
    def pollSolutionFinder(self):
        ok=True
        grown=False
        while ok:
            try:
                s=self.sf.solutionQueue.get_nowait()
            except Empty:
                ok=False
            else:
                self.sf.solutionQueue.task_done()
                self.solutions.append(s)
                grown=True
                
        if grown:
            self.updateSolutionDisplay()

        if not self.sf.workQueue.empty() and not self.sf.solutionQueue.empty():
            QtCore.QTimer.singleShot(500, self.pollSolutionFinder)
            
    def updateSolutionDisplay(self):
        for n, s in enumerate(self.solutions):
            self.SolutionChooser.setItem(n, 0, QtGui.QTableWidgetItem('%.4f'%s.solutionScore()))
            self.SolutionChooser.setItem(n,  1, QtGui.QTableWidgetItem('%.4f'%s.angularDeviation()))
