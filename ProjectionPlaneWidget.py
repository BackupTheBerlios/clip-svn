from ToolBox import StereoProjector,  Vec3D,  Mat3D

from PyQt4 import QtCore, QtGui
import math



class ProjectionPlaneWidget(QtGui.QWidget):
    def __init__(self, o, parent):
        QtGui.QWidget.__init__(self, parent)
        self.projector=StereoProjector(o)
        self.projector.setWavelength(0.7, 1000.0)
        self.connect(self.projector, QtCore.SIGNAL('projectedPointsUpdated()'),  self.updatePoints)
        self.setMinimumSize(QtCore.QSize(100, 100))
        self.setAcceptDrops(True)
        self.gs=QtGui.QGraphicsScene(QtCore.QRectF(-1.0, -1.0, 2.0, 2.0), self)
        self.gv=MyGraphicsView(self.gs, self)
        self.gv.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gv.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gv.setRenderHints(QtGui.QPainter.Antialiasing)

    def resizeEvent(self, e):
        l=min(self.width(), self.height())
        self.gv.setGeometry(0.5*(self.width()-l),  0.5*(self.height()-l), l, l)
        
#    def paintEvent(self, e):
    def updatePoints(self):
        self.gs.clear()
        r=QtCore.QRectF(0, 0, 0.015,  0.015)
        
        self.marker=self.gs.addItem(PrimaryBeamMarker(0.01, 0.05))
        
        #b=QtCore.QRectF(-1.02, -1.02, 2.04,  2.04)
        for x in self.projector.projectedPoints:
            r.moveCenter(x)
            #if b.contains(r):
            self.gs.addEllipse(r, QtCore.Qt.green)
        self.gv.fitInView(self.gv.sceneRect())
         
    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('application/CrystalPointer'):
            e.acceptProposedAction()
            
    def dropEvent(self, e):
        e.acceptProposedAction()
        c=e.source().crystal
        self.projector.connectToCrystal(c)

class MyGraphicsView(QtGui.QGraphicsView):
    def __init__(self, gs, parent=0):
        QtGui.QGraphicsView.__init__(self, gs, parent)
        self.zoomStart=None
        self.rubberBand=self.rubberBand=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.zoomSteps=[]
        
    def mousePressEvent(self, e):
        QtGui.QGraphicsView.mousePressEvent(self, e)
        if not e.isAccepted():
            if e.buttons()==QtCore.Qt.LeftButton:
                self.zoomStart=self.mapToScene(e.pos())
                e.accept()
                
                self.rubberBand.setGeometry(QtCore.QRect(e.pos(), e.pos()).normalized())
                self.rubberBand.show()
            elif e.buttons()==QtCore.Qt.RightButton:
                try:
                    self.zoomSteps.pop()
                    self.updateZoom()
                except:
                    pass
        
    def mouseMoveEvent(self, e):
        if self.zoomStart==None: 
            QtGui.QGraphicsView.mouseMoveEvent(self, e)
        else:
            self.rubberBand.setGeometry(QtCore.QRect(self.mapFromScene(self.zoomStart), e.pos()).normalized())
            
    def mouseReleaseEvent(self, e):
        if self.zoomStart==None: 
            QtGui.QGraphicsView.mouseReleaseEvent(self, e)
        else:
            self.rubberBand.hide()
            self.zoomSteps.append(QtCore.QRectF(self.zoomStart, self.mapToScene(e.pos())).normalized())
            self.updateZoom()
            self.zoomStart=None

        
    def resizeEvent(self, e):
        
        QtGui.QGraphicsView.resizeEvent(self, e)
        self.updateZoom()
        
    def updateZoom(self):
        if len(self.zoomSteps)>0:
            self.fitInView(self.zoomSteps[-1], QtCore.Qt.KeepAspectRatio)
        else:
            self.fitInView(self.scene().sceneRect())
            
    def dragEnterEvent(self, e):
        if not e.mimeData().hasFormat('application/CrystalPointer'):
            QtGui.QGraphicsView.dragEnterEvent(self, e)
            

class SignalingEllipse(QtCore.QObject, QtGui.QGraphicsEllipseItem):
    def __init__(self, *args):
        QtGui.QGraphicsEllipseItem.__init__(self, *args)
        QtCore.QObject.__init__(self)
        
    def itemChange(self, c, v):
        if c==QtGui.QGraphicsItem.ItemPositionChange:
            self.emit('posChanged()')
        return v
        

class PrimaryBeamMarker(SignalingEllipse):
    def __init__(self, size, radius, parent=None):
        SignalingEllipse.__init__(self, parent)
        
        r=QtCore.QRectF(-size, -size, 2*size, 2*size)
        self.setRect(r)
        r.translate(radius, 0)
        self.handle=SignalingEllipse(self)
        self.handle.setRect(r)
        self.marker=QtGui.QGraphicsEllipseItem(self)

        for w in (self,  self.handle):
            w.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

        for w in (self, self.marker,  self.handle):
            w.setPen(QtCore.Qt.red)
            
        self.updateSize()
        self.setCursor(QtCore.Qt.SizeAllCursor)
        self.handle.setCursor(QtCore.Qt.SizeAllCursor)
        self.connect(self.handle, QtCore.SIGNAL('posChanged()'),  self.updateSize)
        
    def updateSize(self):
        p=self.handle.rect().center()-self.rect().center()
        l=math.hypot(p.x(), p.y())
        r=QtCore.QRectF(-l, -l, 2*l, 2*l)
        r.translate(self.marker.rect().center())
        self.marker.setRect(r)
        
