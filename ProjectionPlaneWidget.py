from ToolBox import StereoProjector,  Vec3D,  Mat3D

from PyQt4 import QtCore, QtGui

class ProjectionPlaneWidget(QtGui.QWidget):
    def __init__(self, o, parent):
        QtGui.QWidget.__init__(self, parent)
        self.projector=StereoProjector(o)
        self.connect(self.projector, QtCore.SIGNAL('projectedPointsUpdated()'),  self.update)
        self.setMinimumSize(QtCore.QSize(50, 50))
    

    def paintEvent(self, e):
        p=QtGui.QPainter(self)
        l=min(self.width(), self.height())
        p.translate(0.5*self.width(), 0.5*self.height())
        p.fillRect(QtCore.QRectF(-0.5*l, -0.5*l, l, l),  QtCore.Qt.black)
        p.scale(0.5*l, 0.5*l)
        r=QtCore.QRectF(0, 0, 5.0/l,  5.0/l)
        p.setPen(QtCore.Qt.green)
        for x in self.projector.projectedPoints:
            r.moveCenter(x)
            p.drawEllipse(r)
