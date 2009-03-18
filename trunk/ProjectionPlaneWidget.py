from ToolBox import StereoProjector, LauePlaneProjector, Vec3D, Mat3D, ImageTransfer, Crystal
import LaueImage
from PyQt4 import QtCore, QtGui
import math
from time import time

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
        self.setMinimumSize(QtCore.QSize(200, 240))
        self.setAcceptDrops(True)

        self.gv=MyGraphicsView(self)
        self.gv.setScene(self.projector.getScene())
        self.gv.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        self.connect(self.projector, QtCore.SIGNAL('wavevectorsUpdated()'),  self.gv.update)
        self.connect(self.projector, QtCore.SIGNAL('imgTransformUpdated()'),  self.resizeView)
        self.connect(self.projector, QtCore.SIGNAL('imgTransformUpdated()'),  self.updateZoom)

    #self.connect(self.projector, QtCore.SIGNAL('projectionRectPosChanged()'),  self.updateZoom)
        self.toolBar=QtGui.QToolBar(self)
        
        a=self.mkActionGroup(0, ((':/zoom.png', 'Zoom'), (':/pan.png', 'Pan'), (':/rotate_left.png', 'Rotate')))
        
        self.connect(a[0], QtCore.SIGNAL('toggled(bool)'), self.zoomHandler)
        self.connect(a[1], QtCore.SIGNAL('toggled(bool)'), self.panHandler)
        self.connect(a[2], QtCore.SIGNAL('toggled(bool)'), self.rotateHandler)
        
        self.toolBar.addSeparator()
        a=self.mkActionGroup(0, ((':/info.png', 'Info'), (':/flag.png', 'Add Marker')))
        self.connect(a[0], QtCore.SIGNAL('toggled(bool)'), self.infoHandler)
        self.connect(a[1], QtCore.SIGNAL('toggled(bool)'), self.markHandler)

        self.toolBar.addSeparator()
        
        self.imageAction=self.toolBar.addAction(QtGui.QIcon(':/fileopen.png'), 'Load Image', self.slotLoadCloseImage)
        self.toolBar.addAction(QtGui.QIcon(':/fileprint.png'), 'Print', self.slotPrint)

        self.toolBar.addSeparator()
        a=self.toolBar.addAction(QtGui.QIcon(':/configure.png'), 'Configure')
        self.connect(a, QtCore.SIGNAL('triggered(bool)'), self.startConfig)
    
        self.rubberBand=QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,  self.gv)
        
        self.mouseHandler=self.zoomHandler
        self.mousePressHandler=self.infoHandler
        QtCore.QTimer.singleShot(0, self.startResize)
        self.grip=QtGui.QSizeGrip(self)
        self.setWindowIcon(QtGui.QIcon(':/Projector.png'))
        
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
            a=self.toolBar.addAction(QtGui.QIcon(icon), text)
            a.setCheckable(True)
            group.addAction(a)
            r.append(a)
        r[n].setChecked(True)
        return r

    def startResize(self):
        self.resize(self.width()+1, self.height())
        
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
        fullScene=self.projector.getScene().sceneRect().size()
        fullScene*=scaleFactor
        maxScene=fullScene.boundedTo(spareSize)
        maxSceneRect=QtCore.QRectF(QtCore.QPointF(0.5*(self.width()-maxScene.width()), 0.5*(self.height()-maxScene.height()+toolBarGeometry.height())), maxScene)
        self.gv.setGeometry(maxSceneRect.toRect())
        p=self.rect().bottomRight()
        self.grip.move(p.x()-self.grip.width(), p.y()-self.grip.height())

         
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
                    self.mousePressHandler()
                            
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
            setRotAxis=menu.addAction("Set Rotation Axis")
            clearInfo=menu.addAction("Clear Reflex Infos")
            clearMarker=menu.addAction("Clear Nearest Marker")
            clearAllMarker=menu.addAction("Clear All Marker")
            r=menu.exec_(self.gv.mapToGlobal(self.lastMousePos), setRotAxis)
            if r==clearMarker:
                self.projector.delMarkerNear(self.gv.mapToScene(self.lastMousePos))
            elif r==setRotAxis:
                c=self.projector.getCrystal()
                if c:
                    r=c.getClosestReflection(self.projector.det2normal(self.gv.mapToScene(self.lastMousePos))[0])
                    c.setRotationAxis(Vec3D(r.h, r.k, r.l), Crystal.ReziprocalSpace)
            elif r==clearInfo:
                self.projector.clearInfoItems()
            elif r==clearAllMarker:
                while self.projector.markerNumber()>0:
                    self.projector.delMarkerNear(self.projector.getMarkerDetPos(0))
        
            self.mousePressStart=None

    def zoomRect(self):
        if len(self.zoomSteps)>0:
            return self.projector.img2det.mapRect(self.zoomSteps[-1])
        else:
            return self.gv.scene().sceneRect()
        
    def updateZoom(self):
        #self.gv.fitInView(self.zoomRect(), QtCore.Qt.KeepAspectRatio)
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
                v1, b1=self.projector.det2normal(p1)
                v2, b2=self.projector.det2normal(p2)
                if b1 and b2:
                    r=v1%v2
                    r.normalize()
                    a=math.acos(v1*v2)
                    self.projector.addRotation(r, a)
                    # Process screen updates. Otherwise no updates are prosessed if
                    # two projectors are active and the mouse moves fast
                    QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def rotateHandler(self, *args):
        if len(args)==1 and args[0]:
            self.mouseHandler=self.rotateHandler
        elif len(args)==2:
            e, context=args
            if context==self.moveContext:
                p1=self.gv.mapToScene(self.lastMousePos)
                p2=self.gv.mapToScene(self.gv.mapFromParent(e.pos()))
                v1, b1=self.projector.det2normal(p1)
                v2, b2=self.projector.det2normal(p2)
                c=self.projector.getCrystal()
                if c and b1 and b2:
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

    def infoHandler(self, *args):
        def f(i):
            if i<0:
                return '<span style="text-decoration:overline">%i</span>'%(-i)
            else :
                return '<span>%i</span>'%i
                
        if len(args)==1 and args[0]:
            self.mousePressHandler=self.infoHandler
        elif len(args)==0:
            c=self.projector.getCrystal()
            if c:
                p=self.gv.mapToScene(self.mousePressStart)
                r=c.getClosestReflection(self.projector.det2normal(p)[0])
                s=f(r.h)+f(r.k)+f(r.l)
                if r.normal[0]>=0:
                    TT=180.0-2.0*math.degrees(math.acos(max(-1, min(1, r.normal[0]))))
                    s+='<br>2T=%.1f'%TT
                self.projector.addInfoItem(s, p)
                self.emit(QtCore.SIGNAL('reflexInfo(int,int,int)'), r.h, r.k, r.l)

    def markHandler(self, *args):
        if len(args)==1 and args[0]:
            self.mousePressHandler=self.markHandler
        elif len(args)==0:
            self.projector.addMarker(self.gv.mapToScene(self.mousePressStart))

                
    def slotLoadCloseImage(self):
        if self.image==None:
          fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Load Laue pattern', '', 'Image Plate Files (*.img);;All Images (*.jpg *.jpeg *.bmp *.png *.tif *.tiff *.gif *.img);;All Files (*)'))
          fInfo=QtCore.QFileInfo(fileName)
          if fInfo.exists():
            img=LaueImage.Image.open(fileName)
            mode=None
            if img.mode=='RGB':
                mode=1
            elif img.mode=='F':
                mode=0
            elif img.mode=='L':
                img=img.convert('F')
                mode=0

            if mode!=None:
                self.image=ImageTransfer()
                self.image.setData(img.size[0], img.size[1], mode, img.tostring())
                if hasattr(img, 'resx') and hasattr(img, 'resy'):
                    self.projector.setDetSize(self.projector.dist(), img.width/img.resx, img.height/img.resy)
                self.gv.setBGImage(self.image)
                self.gv.resetCachedContent()
                self.gv.viewport().update()
                self.imageAction.setIcon(QtGui.QIcon(':/fileclose.png'))
                self.imageAction.setIconText('Close Image')
        else:
            self.gv.setBGImage(None)
            self.image=None
            self.imageAction.setIcon(QtGui.QIcon(':/fileopen.png'))
            self.imageAction.setIconText('Open Image')
            self.gv.resetCachedContent()
            self.gv.viewport().update()

    def slotPrint(self):
        pr=QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        pd=QtGui.QPrintDialog(pr,  self)
        pd.setWindowTitle('Print Projection')
        if pd.exec_()==QtGui.QDialog.Accepted:
            p=QtGui.QPainter(pr)
            p.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing|QtGui.QPainter.SmoothPixmapTransform)
            self.gv.render(p)
            p.end()
            
            




















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

            t1=time()
            qi=self.BGImage.qImg()
            t2=time()

            sr=self.sceneRect()
            source=QtCore.QRectF((to.x()-sr.x())*qi.width()/sr.width(), (to.y()-sr.y())*qi.height()/sr.height(), to.width()*qi.width()/sr.width(), to.height()*qi.height()/sr.height())
            t3=time()
            
            p.drawImage(to, qi, source)
            t4=time()
            print 'Convert Times', t2-t1, t3-t2, t4-t3
            p.restore()
