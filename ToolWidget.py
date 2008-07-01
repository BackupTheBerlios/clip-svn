from PyQt4 import QtCore, QtGui
from Crystal import Crystal as CrystalObject
from ProjectionPlaneWidget import ProjectionPlaneWidget as ProjectionObject

class ToolWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,  parent)

        
    def closeEvent(self, e):
        #e.ignore()
        #self.parent().hide()
        pass
    
    def searchCrystal(self):
        try:
            mdi=self.parent().mdiArea()
        except:
            return
        windows=mdi.subWindowList(QtGui.QMdiArea.ActivationHistoryOrder)
        windows.reverse()
        for w in windows:
            if isinstance(w.widget(), CrystalObject):
                return w.widget().crystal
            elif isinstance(w.widget(), ProjectionObject):
                return w.widget().projector.getCrystal()
        return None
    
