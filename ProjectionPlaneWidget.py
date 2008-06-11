from ToolBox import StereoProjector,  Vec3D,  Mat3D

from PyQt4 import QtCore, QtGui
import math

from Tools import Icons

class ProjectionPlaneWidget(QtGui.QWidget):
    pressContext=1
    moveContext=2
    releaseContext=3
    def __init__(self, o, parent):
        QtGui.QWidget.__init__(self, parent)

        self.zoomSteps=[]
        self.mousePressStart=None
        
        self.projector=StereoProjector(o)
        self.projector.setWavelength(0.7, 1000.0)
        self.connect(self.projector, QtCore.SIGNAL('projectedPointsUpdated()'),  self.updatePoints)
        self.setMinimumSize(QtCore.QSize(140, 180))
        self.setAcceptDrops(True)

        #TODO: Move scene to projector
        self.gs=QtGui.QGraphicsScene(QtCore.QRectF(-1.0, -1.0, 2.0, 2.0), self)

        self.gv=MyGraphicsView(self)
        self.gv.setScene(self.gs)

        self.toolBar=QtGui.QToolBar(self)
        
        a=self.mkActionGroup(0, ((Icons.viewmag, 'Zoom'), (Icons.rotate, 'Pan'), (Icons.rotate, 'Rotate')))
        self.toolBar.addSeparator()
        self.mkActionGroup(0, ((Icons.messagebox_info, 'Info'), (Icons.messagebox_info, 'AddMarker')))
        self.toolBar.addSeparator()
        self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.configure)), 'configure')
        
        self.connect(a[0],  QtCore.SIGNAL('toggled(bool)'),  self.zoomHandler)
        self.connect(a[1],  QtCore.SIGNAL('toggled(bool)'),  self.panHandler)
        self.connect(a[2],  QtCore.SIGNAL('toggled(bool)'),  self.rotateHandler)
        
        self.rubberBand=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,  self.gv)
        
        self.mouseHandler=self.zoomHandler

    def mkActionGroup(self, n, args):
        group=QtGui.QActionGroup(self)
        r=[]
        for icon, text in args:
            a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(icon)), text)
            a.setCheckable(True)
            group.addAction(a)
            r.append(a)
        r[n].setChecked(True)
        return r

    def resizeEvent(self, e):
        self.resizeView()
        self.updateZoom()
        
    def resizeView(self):
        toolBarGeometry=QtCore.QRect(0, 0, self.width(),  self.toolBar.sizeHint().height())
        self.toolBar.setGeometry(toolBarGeometry)
        spareSize=QtCore.QSizeF(self.width(),  self.height()-toolBarGeometry.height())
        scaledZoom=self.zoomRect().size()
        scaledZoom.scale(spareSize, QtCore.Qt.KeepAspectRatio)
        scaleFactor=scaledZoom.width()/self.zoomRect().width()
        fullScene=self.gs.sceneRect().size()
        fullScene*=scaleFactor
        maxScene=fullScene.boundedTo(spareSize)
        maxSceneRect=QtCore.QRectF(QtCore.QPointF(0.5*(self.width()-maxScene.width()), 0.5*(self.height()-maxScene.height()+toolBarGeometry.height())), maxScene)
        self.gv.setGeometry(maxSceneRect.toRect())
        
    #TODO: Move to projector
    def updatePoints(self):
        self.gs.clear()
        r=QtCore.QRectF(0, 0, 0.015,  0.015)
        
        self.marker=self.gs.addEllipse(r,  QtCore.Qt.red)
        self.marker.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.marker.setCursor(QtCore.Qt.SizeAllCursor)
        bounding=self.gs.sceneRect()
        for x in self.projector.projectedPoints:
            if bounding.contains(x):
                r.moveCenter(x)
                self.gs.addEllipse(r, QtCore.Qt.green)
         
    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('application/CrystalPointer'):
            e.acceptProposedAction()
            
    def dropEvent(self, e):
        e.acceptProposedAction()
        c=e.source().crystal
        self.projector.connectToCrystal(c)

    def mousePressEvent(self, e):
        if self.gv.geometry().contains(e.pos()):
            self.mousePressStart=self.gv.mapFromParent(e.pos())
            self.mouseButtons=e.buttons()
            self.lastMousePos=self.gv.mapFromParent(e.pos())
            if e.buttons()==QtCore.Qt.LeftButton:
                self.mouseHandler(e, self.pressContext)
            elif e.buttons()==QtCore.Qt.RightButton:
                QtCore.QTimer.singleShot(QtGui.QApplication.startDragTime(),  self.showContextMenu)

    def mouseMoveEvent(self, e):
        if self.mousePressStart!=None and self.gv.geometry().contains(e.pos()):
            if e.buttons()==QtCore.Qt.LeftButton:
                self.mouseHandler(e, self.moveContext)
        self.lastMousePos=self.gv.mapFromParent(e.pos())
        
    def mouseReleaseEvent(self, e):
        if self.mousePressStart!=None and self.gv.geometry().contains(e.pos()):
            if self.mouseButtons==QtCore.Qt.LeftButton:
                a, b=[self.gv.mapToScene(x) for x in (self.mousePressStart,  self.gv.mapFromParent(e.pos()))]
                r=QtCore.QRectF(a, b).normalized()
                if (1000*r.width()>self.gv.sceneRect().width() and 1000*r.height()>self.gv.sceneRect().height()):
                    self.mouseDragRect=r
                    self.mouseHandler(e, self.releaseContext)
            elif self.mouseButtons==QtCore.Qt.RightButton:
                if len(self.zoomSteps):
                    self.zoomSteps.pop()
                    self.resizeView()
                    self.updateZoom()
            self.rubberBand.hide()
            self.mousePressStart=None

    def showContextMenu(self):
        if self.mousePressStart!=None:
            print 'ContextMenu'
            self.mousePressStart=None

    def zoomRect(self):
        if len(self.zoomSteps)>0:
            return self.zoomSteps[-1]
        else:
            return self.gv.scene().sceneRect()
        
    def updateZoom(self):
        self.gv.fitInView(self.zoomRect(), QtCore.Qt.KeepAspectRatio)

    def zoomHandler(self, *args):
        if len(args)==1 and args[0]:
            self.mouseHandler=self.zoomHandler
        elif len(args)==2:
            e, context=args
            if context==self.pressContext:
                self.rubberBand.setGeometry(QtCore.QRect(e.pos(), e.pos()).normalized())
                self.rubberBand.show()
            elif context==self.moveContext:
                self.rubberBand.setGeometry(QtCore.QRect(self.mousePressStart, self.gv.mapFromParent(e.pos())).normalized())
            elif context==self.releaseContext:
                self.zoomSteps.append(self.mouseDragRect)
                self.resizeView()
                self.updateZoom()


        
    def panHandler(self, *args):
        if len(args)==1 and args[0]:
            self.mouseHandler=self.panHandler
        elif len(args)==2:
            e, context=args
            if context==self.moveContext:
                p1=self.gv.mapToScene(self.lastMousePos)
                p2=self.gv.mapToScene(self.gv.mapFromParent(e.pos()))
                v1=self.projector.det2normal(p1)
                v2=self.projector.det2normal(p2)
                r=v2%v1
                r.normalize()
                a=math.acos(v1*v2)
                #print '%6.3f %6.3f %6.3f %6.3f'%(p1.x(),  p1.y(),  p2.x(), p2.y()), v1, v2, r, a
                print v2, r
                self.projector.addRotation(r, a)

    def rotateHandler(self, *args):
        if len(args)==1 and args[0]:
            self.mouseHandler=self.rotateHandler
        elif len(args)==2:
            e, context=args
            if context==self.pressContext:
                pass


class MyGraphicsView(QtGui.QGraphicsView):
    def __init__(self, parent=0):
        QtGui.QGraphicsView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setDragMode(self.NoDrag)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.viewIgnoresThisMouseEvent=False
        
    def dragEnterEvent(self, e):
        if not e.mimeData().hasFormat('application/CrystalPointer'):
            QtGui.QGraphicsView.dragEnterEvent(self, e)
            
    def mousePressEvent(self, e):
        QtGui.QGraphicsView.mousePressEvent(self, e)
        if not e.isAccepted():
            print 'Ignored'
            self.viewIgnoresThisMouseEvent=True
            
    def mouseMoveEvent(self, e):
        if self.viewIgnoresThisMouseEvent:
            e.ignore()
        else:
            QtGui.QGraphicsView.mouseMoveEvent(self, e)

    def mouseReleaseEvent(self, e):
        if self.viewIgnoresThisMouseEvent:
            e.ignore()
            self.viewIgnoresThisMouseEvent=False
        else:
            QtGui.QGraphicsView.mouseReleaseEvent(self, e)



#FIXME: Port to C++ and remove here

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
        
