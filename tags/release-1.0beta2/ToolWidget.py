from PyQt4 import QtCore, QtGui
from Crystal import Crystal as CrystalObject
from ProjectionPlaneWidget import ProjectionPlaneWidget as ProjectionObject

class ToolWidget(QtGui.QWidget):
    def __init__(self, menuName, parent=None):
        QtGui.QWidget.__init__(self,  parent)
        self.menuName=menuName
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        if parent:
            self.connect(parent.MdiArea, QtCore.SIGNAL('subWindowActivated(QMdiSubWindow*)'),  self.windowChanged)
            self.MdiArea=parent.MdiArea
        self.hide()
        
    def closeEvent(self, e):
        e.ignore()
        self.parent().deleteLater()
        self.MdiArea.removeSubWindow(self)
        print "Tool close"
    
    def searchCrystal(self):
        windows=self.MdiArea.subWindowList(QtGui.QMdiArea.ActivationHistoryOrder)
        windows.reverse()
        for w in windows:
            if isinstance(w.widget(), CrystalObject):
                return w.widget().crystal
            elif isinstance(w.widget(), ProjectionObject):
                return w.widget().projector.getCrystal()
        return None
    
    def searchImage(self):
        windows=self.MdiArea.subWindowList(QtGui.QMdiArea.ActivationHistoryOrder)
        windows.reverse()
        for w in windows:
            if isinstance(w.widget(), ProjectionObject) and w.widget().image:
                return w.widget()
        return

    def searchProjector(self):
        windows=self.MdiArea.subWindowList(QtGui.QMdiArea.ActivationHistoryOrder)
        windows.reverse()
        for w in windows:
            if isinstance(w.widget(), ProjectionObject):
                return w.widget()
        return

    def showWindow(self):
        for mdi in self.MdiArea.subWindowList():
            if mdi.widget()==self:
                self.MdiArea.setActiveSubWindow(mdi)
                return
        mdi=self.MdiArea.addSubWindow(self)
        mdi.show()
        self.show()
        
    def windowChanged(self):
        pass
        
    def rotAxisChanged(self):
        pass
        
    def orientationChanged(self):
        pass
        
    def reflexInfo(self, h, k, l):
        pass
        
    def addedRotation(self, d):
        pass
