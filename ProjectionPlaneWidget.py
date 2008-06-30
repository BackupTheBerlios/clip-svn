from ToolBox import StereoProjector, LauePlaneProjector, Vec3D, Mat3D, ImageTransfer
import LaueImage
from PyQt4 import QtCore, QtGui
import math

from Tools import Icons

class ProjectionPlaneWidget(QtGui.QWidget):
    pressContext=1
    moveContext=2
    releaseContext=3
    def __init__(self, type, parent):
        QtGui.QWidget.__init__(self, parent)

        self.zoomSteps=[]
        self.mousePressStart=None
        self.image=None
        
        if type==0:
            self.projector=StereoProjector(self)
        elif type==1:
            self.projector=LauePlaneProjector(self)
        self.setMinimumSize(QtCore.QSize(140, 180))
        self.setAcceptDrops(True)

        self.gv=MyGraphicsView(self)
        self.gv.setScene(self.projector.getScene())
        self.gv.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        self.connect(self.projector, QtCore.SIGNAL('wavevectorsUpdated()'),  self.gv.update)
        self.connect(self.projector, QtCore.SIGNAL('imgTransformUpdated()'),  self.resizeView)
        self.connect(self.projector, QtCore.SIGNAL('imgTransformUpdated()'),  self.updateZoom)

    #self.connect(self.projector, QtCore.SIGNAL('projectionRectPosChanged()'),  self.updateZoom)
        self.toolBar=QtGui.QToolBar(self)
        
        a=self.mkActionGroup(0, ((Icons.viewmag, 'Zoom'), (Icons.rotate, 'Pan'), (Icons.rotate, 'Rotate')))
        
        self.connect(a[0], QtCore.SIGNAL('toggled(bool)'), self.zoomHandler)
        self.connect(a[1], QtCore.SIGNAL('toggled(bool)'), self.panHandler)
        self.connect(a[2], QtCore.SIGNAL('toggled(bool)'), self.rotateHandler)
        
        self.toolBar.addSeparator()
        self.mkActionGroup(0, ((Icons.messagebox_info, 'Info'), (Icons.messagebox_info, 'Add Marker')))

        self.toolBar.addSeparator()
        
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.fileopen)), 'Load Image')
        self.connect(a, QtCore.SIGNAL('triggered(bool)'), self.slotLoadImage)
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.fileclose)), 'Close Image')
        self.connect(a, QtCore.SIGNAL('triggered(bool)'), self.slotCloseImage)


        self.toolBar.addSeparator()
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.configure)), 'Configure')
        self.connect(a, QtCore.SIGNAL('triggered(bool)'), self.startConfig)
    
        self.rubberBand=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,  self.gv)
        
        self.mouseHandler=self.zoomHandler
        QtCore.QTimer.singleShot(0, self.startResize)
        
            
        
    def startConfig(self):
        s=self.projector.configName()
        #try:
        exec('from %s import %s'%(s, s))
        w=eval('%s(self.projector,self.gv,self)'%s)
        #except:
        #  pass
        #else:           
        mdi=self.parent().mdiArea()
        mdi.addSubWindow(w)
        w.show()
            

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

    def startResize(self):
        #FIXME: View not fixed
        self.resize(self.width()+1, self.height())
        
    def resizeEvent(self, e):
        self.resizeView()
        self.updateZoom()
        
    def resizeView(self):
        print "resizeView"
        toolBarGeometry=QtCore.QRect(0, 0, self.width(),  self.toolBar.sizeHint().height())
        self.toolBar.setGeometry(toolBarGeometry)
        spareSize=QtCore.QSizeF(self.width(),  self.height()-toolBarGeometry.height())
        scaledZoom=self.zoomRect().size()
        scaledZoom.scale(spareSize, QtCore.Qt.KeepAspectRatio)
        scaleFactor=scaledZoom.width()/self.zoomRect().width()
        fullScene=self.projector.getScene().sceneRect().size()
        fullScene*=scaleFactor
        maxScene=fullScene.boundedTo(spareSize)
        maxSceneRect=QtCore.QRectF(QtCore.QPointF(0.5*(self.width()-maxScene.width()), 0.5*(self.height()-maxScene.height()+toolBarGeometry.height())), maxScene)
        self.gv.setGeometry(maxSceneRect.toRect())
        

         
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
                else:
                    # Mouse just pressed, no drag...
                    self.projector.addMarker(self.gv.mapToScene(self.mousePressStart))
            elif self.mouseButtons==QtCore.Qt.RightButton:
                if len(self.zoomSteps):
                    self.zoomSteps.pop()
                    self.resizeView()
                    self.updateZoom()
            self.rubberBand.hide()
            self.mousePressStart=None

    def showContextMenu(self):
        if self.mousePressStart!=None:
            menu=QtGui.QMenu(self)
            clearMarker=menu.addAction("Clear marker")
            setRotAxis=menu.addAction("Set rotation Axis")
            r=menu.exec_(self.gv.mapToGlobal(self.lastMousePos))
            if r==clearMarker:
                self.projector.delMarkerNear(self.gv.mapToScene(self.lastMousePos))
            elif r==setRotAxis:
                pass
                #FIXME: Implement
            self.mousePressStart=None

    def zoomRect(self):
        if len(self.zoomSteps)>0:
            return self.projector.img2det.mapRect(self.zoomSteps[-1])
        else:
            return self.gv.scene().sceneRect()
        
    def updateZoom(self):
        #self.gv.fitInView(self.zoomRect(), QtCore.Qt.KeepAspectRatio)
        print "updateZoom"
        r=self.zoomRect()
        self.gv.fitInView(r, QtCore.Qt.KeepAspectRatio)
        r=self.gv.scene().sceneRect()
        self.gv.setSceneRect(r)
        
        
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
                r=self.projector.det2img.mapRect(self.mouseDragRect)
                self.zoomSteps.append(r)
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
                r=v1%v2
                r.normalize()
                a=math.acos(v1*v2)
                self.projector.addRotation(r, a)

    def rotateHandler(self, *args):
        if len(args)==1 and args[0]:
            self.mouseHandler=self.rotateHandler
        elif len(args)==2:
            e, context=args
            if context==self.moveContext:
                p1=self.gv.mapToScene(self.lastMousePos)
                p2=self.gv.mapToScene(self.gv.mapFromParent(e.pos()))
                v1=self.projector.det2normal(p1)
                v2=self.projector.det2normal(p2)
                c=self.projector.getCrystal()
                if c:
                    ax=c.getLabSystamRotationAxis()
                    v1=v1-ax*(v1*ax)
                    v2=v2-ax*(v2*ax)
                    v1.normalize()
                    v2.normalize()
                    a=math.acos(min(1, v1*v2))
                    if Mat3D(ax, v1, v2).det()<0:
                        a*=-1
                    self.projector.addRotation(ax, a)
                    self.emit(QtCore.SIGNAL('projectorAddedRotation(double)'), a)

                
    def slotLoadImage(self):
      fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Load Laue pattern', '', 'Image Plate Files (*.img);;All Images (*.jpg *.jpeg *.bmp *.png *.tif *.tiff *.gif *.img);;All Files (*)'))
      fInfo=QtCore.QFileInfo(fileName)
      if fInfo.exists():
        img=LaueImage.Image.open(fileName)
        mode=None
        if img.mode=='RGB':
            mode=1
        elif img.mode=='F':
            mode=0
        if mode!=None:
            self.image=ImageTransfer()
            for i in range(4):
                self.image.setTransferCurve(i, [1.], [0., 1., 0., 0.])
            self.image.setData(img.width, img.height, mode, img.tostring())
            if hasattr(img, 'resx') and hasattr(img, 'resy'):
                self.projector.setDetSize(self.projector.dist(), img.width/img.resx, img.height/img.resy)
            self.gv.setBGImage(self.image)
            self.gv.resetCachedContent()
            self.gv.viewport().update()
            
    def slotCloseImage(self):
        self.gv.setBGImage(None)

class MyGraphicsView(QtGui.QGraphicsView):
    def __init__(self, parent=0):
        QtGui.QGraphicsView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.SmoothPixmapTransform)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setDragMode(self.NoDrag)
        #self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.viewIgnoresThisMouseEvent=False
        self.BGImage=None
        
    def dragEnterEvent(self, e):
        if not e.mimeData().hasFormat('application/CrystalPointer'):
            QtGui.QGraphicsView.dragEnterEvent(self, e)
            
    def mousePressEvent(self, e):
        if e.buttons()==QtCore.Qt.LeftButton:
            QtGui.QGraphicsView.mousePressEvent(self, e)
            if not e.isAccepted():
                self.viewIgnoresThisMouseEvent=True
        else:
            self.viewIgnoresThisMouseEvent=True
            e.ignore()
            
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

    def setBGImage(self, img):
        self.BGImage=img
        self.viewport().update()
        
    def drawBackground(self, p, to):
        if self.BGImage==None:
            QtGui.QGraphicsView.drawBackground(self, p, to)
        else:
            p.save()
            #p.setClipRect(to)
            qi=self.BGImage.qImg()
            sr=self.sceneRect()
            source=QtCore.QRectF((to.x()-sr.x())*qi.width()/sr.width(), (to.y()-sr.y())*qi.height()/sr.height(), to.width()*qi.width()/sr.width(), to.height()*qi.height()/sr.height())
            
            p.drawImage(to, qi, source)
            p.restore()
