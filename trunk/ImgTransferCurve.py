from Ui_ImgTransferCurve import Ui_ImgTransferCurve
from PyQt4 import QtCore, QtGui
from ToolBox import SignalingEllipseItem, BezierCurve
from ToolWidget import ToolWidget


class ImgTransferCurve(ToolWidget, Ui_ImgTransferCurve):
    def __init__(self, parent):
        ToolWidget.__init__(self, 'Image Transver Curve', parent)
        self.setupUi(self)
        self.connect(self.ColorSelector,  QtCore.SIGNAL('activated(int)'),  self.colorSelChanged)
        self.toDelete=[]
        # PlotDisplay Setup
        self.gs=QtGui.QGraphicsScene()
        self.gs.setSceneRect(0, 0, 1, 1)
        self.gs.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.gv.setScene(self.gs)
        #self.gv.translate(0, -1)
        self.gv.scale(1, -1)
        self.gv.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gv.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gv.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.SmoothPixmapTransform)
        self.gv.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.gv.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)        
        
        linePen=QtGui.QPen(QtCore.Qt.DashLine)
        linePen.setColor(QtCore.Qt.gray)
        for d in (0.0,  0.25,  0.5,  0,.75,  1.0):
            self.gs.addLine(0, d, 1, d, linePen)
            self.gs.addLine(d, 0, d, 1, linePen)

        self.gv.fitInView(0, 0, 1, 1)

        a=self.toolBar.addAction(QtGui.QIcon(':/fileopen.png'), 'Load Curve',  self.loadCurves)
        a=self.toolBar.addAction(QtGui.QIcon(':/filesave.png'), 'Save Curve', self.saveCurves)
        a=self.toolBar.addAction(QtGui.QIcon(':/flip_horizontal.png'), 'Flip Horizontal', self.flipH)
        a=self.toolBar.addAction(QtGui.QIcon(':/flip_vertical.png'), 'Flip Vertical', self.flipV)
        a=self.toolBar.addAction(QtGui.QIcon(':/rotate_right.png'), 'Rotate Clockwise', self.rotCW)
        a=self.toolBar.addAction(QtGui.QIcon(':/rotate_left.png'), 'Rotate Anti-Clockwise', self.rotCCW)

        self.transferCurves=[]
        self.transferCurveMarkers=[[], [], [], []]
        self.bezierCurves=[]
        
        for i, c in enumerate([QtCore.Qt.black, QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.blue]):
            tc=self.gs.addPath(QtGui.QPainterPath())
            p=QtGui.QPen(c)
            p.setCosmetic(True)
            tc.setPen(p)
            self.transferCurves.append(tc)
            
            self.transferCurveMarkers[i].append(self.newMarker(0, 0))
            self.transferCurveMarkers[i].append(self.newMarker(1, 1))
            self.bezierCurves.append(BezierCurve())
            
            for m in self.transferCurveMarkers[i]:
                m.setBoundingBox(QtCore.QRectF(m.pos().x(), 0, 0, 1))
                m.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))            

            self.updateTransferCurve(i)
            
        self.renewTransferCurveMarkers()
        self.makeScales()
        QtCore.QTimer.singleShot(0, self.doResize)
        
        
    
    def updateTransferCurve(self, idx):
        if self.bezierCurves[idx].setPoints([m.pos() for m in self.transferCurveMarkers[idx]]):
            curve=self.bezierCurves[idx]
            N=100
            P=curve.pointRange(0.0,  1.0/N,  N+1)
            path=QtGui.QPainterPath(P[0])
            for p in P[1:]:
                path.lineTo(p)
            self.transferCurves[idx].setPath(path)
            
            
    def publishCurves(self):
        img=self.searchImage()
        if img:
            img.image.setTransferCurves(self.bezierCurves)
            img.gv.resetCachedContent()
            img.gv.viewport().update()
            
            
    def windowChanged(self):
        img=self.searchImage()
        if img:
            for M in self.transferCurveMarkers:
                for m in M:
                    self.gs.removeItem(m)
            c=img.image.getTransferCurves()
            for idx in range(4):
                self.transferCurveMarkers[idx]=[self.newMarker(p.x(), p.y()) for p in c[idx].getPoints()]
                self.updateTransferCurve(idx)
            self.renewTransferCurveMarkers()
            self.makeScales()

    def newMarker(self, x, y):
            m=FixedSignalingEllipseItem()
            m.setRect(-5, -5, 10, 10)
            m.setBoundingBox(self.gs.sceneRect())
            m.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))            
            m.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
            m.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
            vt=self.gv.viewportTransform()
            t=QtGui.QTransform()
            t.scale(1.0/vt.m11(),  1.0/vt.m22())
            m.setTransform(t)
            self.gs.addItem(m)
            self.connect(m, QtCore.SIGNAL('positionChanged()'), self.markerMoved)
            m.setPosNoSig(QtCore.QPointF(x, y))
            return m

    def renewTransferCurveMarkers(self):
        idx=self.ColorSelector.currentIndex()
        for i, M in enumerate(self.transferCurveMarkers):
            for m in M:
                m.setVisible(idx==i)
        
    def markerMoved(self):
        idx=self.ColorSelector.currentIndex()
        self.transferCurveMarkers[idx].sort(lambda x, y:cmp(x.pos().x(),  y.pos().x()))
        self.updateTransferCurve(idx)
        self.makeScales()
        self.publishCurves()
        
    def resizeEvent(self, e):
        self.doResize()
        
    def doResize(self):
        self.gv.fitInView(0, 0, 1, 1)
        vt=self.gv.viewportTransform()
        t=QtGui.QTransform()
        t.scale(1.0/vt.m11(),  1.0/vt.m22())
        for M in self.transferCurveMarkers:
            for m in M:
                m.setTransform(t)
        #self.makeScales()


    def mousePressEvent(self,  e):
        if e.button()==QtCore.Qt.LeftButton:
            p=self.gv.mapFromParent(e.pos())
            if self.rect().contains(p):
                p=self.gv.mapToScene(p)
                idx=self.ColorSelector.currentIndex()
                m=self.newMarker(p.x(), p.y())
                self.transferCurveMarkers[idx].append(m)
                self.transferCurveMarkers[idx].sort(lambda x, y:cmp(x.pos().x(),  y.pos().x()))
                self.updateTransferCurve(idx)
                self.makeScales()
                self.publishCurves()
                p=self.gv.mapFromScene(p)
                me=QtGui.QMouseEvent(e.type(), p, e.globalPos(), e.button(), e.buttons(), e.modifiers())
                self.gv.mousePressEvent(me)
        elif e.button()==QtCore.Qt.RightButton:
            idx=self.ColorSelector.currentIndex()
            for m in self.transferCurveMarkers[idx][1:-1]:
                if m.isUnderMouse():
                    self.transferCurveMarkers[idx].remove(m)
                    self.gs.removeItem(m)
                    self.updateTransferCurve(idx)
                    self.makeScales()
                    self.publishCurves()
            
            
    def colorSelChanged(self,  i):
        self.renewTransferCurveMarkers()
        self.makeScales()


    def flipH(self):
        self.doRot(0,  True)

    def flipV(self):
        self.doRot(2, True)

    def rotCW(self):        
        self.doRot(1, False)

    def rotCCW(self):
        self.doRot(3, False)
    
    def doRot(self, steps, flip):
        img=self.searchImage()
        if img:
            for w in (img.projector, img.image):
                w.doImgRotation(steps,  flip)
            img.gv.viewport().update()
            img.gv.resetCachedContent()
            
            
        
    def makeScales(self):
        pix=QtGui.QPixmap(self.verticalScale.size())
        p=QtGui.QPainter()
        p.begin(pix)
        w=self.verticalScale.width()
        h=self.verticalScale.height()
        
        V=self.bezierCurves[0].range(0.0,  1.0/(h-1), h)
        
        R=self.bezierCurves[1].map(V)
        G=self.bezierCurves[2].map(V)
        B=self.bezierCurves[3].map(V)
        
        for i, (v, r, g, b) in enumerate(zip(V, R, G,  B)):
            i=h-i-1
            v=int(255.0*v)
            r=int(255.0*r)
            g=int(255.0*g)
            b=int(255.0*b)
            p.setPen(QtGui.QColor(r, g, b))
            p.drawLine(0, i, w/2, i)
            if self.ColorSelector.currentIndex()==0:
                p.setPen(QtGui.QColor(v, v, v))
            elif self.ColorSelector.currentIndex()==1:
                p.setPen(QtGui.QColor(r, 0, 0))
            elif self.ColorSelector.currentIndex()==2:
                p.setPen(QtGui.QColor(0, g, 0))
            else:
                p.setPen(QtGui.QColor(0, 0, b))
            p.drawLine(self.verticalScale.width()/2+1, i, self.verticalScale.width(), i)

        p.end()
        self.verticalScale.setPixmap(pix)
        
        pix=QtGui.QPixmap(self.horizontalScale.size())
        p.begin(pix)
        for i in range(self.horizontalScale.width()):
            col=int(255.0/(self.horizontalScale.width()-1)*i)
            p.setPen(QtGui.QColor(col, col, col))
            p.drawLine(i, 0, i, self.horizontalScale.height())
        p.end()
        self.horizontalScale.setPixmap(pix)
        
    def loadCurves(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Choose Curve to load from File', '', 'Clip Curve files (*.curve);;All Files (*)'))
        try:
            import xml.dom.minidom
            doc=xml.dom.minidom.parse(fileName)
            curves=[]
            for i, name in enumerate(('Value', 'Red',  'Green', 'Blue')):
                elem=doc.getElementsByTagName(name)[0]
                points=[]
                for p in elem.getElementsByTagName('Point'):
                    x=float(p.getAttribute('x'))
                    y=float(p.getAttribute('y'))
                    points.append((x, y))
                curves.append(points)
                    
        except:
            pass
        else:
            for n in range(4):
                M=self.transferCurveMarkers[n]
                for m in M:
                    self.gs.removeItem(m)
                self.transferCurveMarkers[n]=[]
                for x, y in curves[n]:
                    self.transferCurveMarkers[n].append(self.newMarker(x, y))
                    
                self.updateTransferCurve(n)
            self.renewTransferCurveMarkers()
            self.makeScales()
            self.publishCurves()
        
    def saveCurves(self):
        import xml.dom.minidom
        doc=xml.dom.minidom.Document()
        base=doc.appendChild(doc.createElement('Transfercurves'))
        for i, name in enumerate(('Value', 'Red',  'Green', 'Blue')):
            curve=base.appendChild(doc.createElement(name))
            for p in self.transferCurveMarkers[i]:
                point=curve.appendChild(doc.createElement('Point'))
                point.setAttribute('x', str(p.pos().x()))
                point.setAttribute('y', str(p.pos().y()))
                
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Choose File to save Curves', '', 'Clip Curve files (*.curve);;All Files (*)')
        if fileName!="":
            doc.writexml(open(fileName, 'w'), addindent='  ',newl='\n')
        
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    def makeHistogram(self, img):
        X=scipy.arange(0.0,  1.0,  1.0/256)
        c1, c2, c3=self.histogramCurves
        h=1.0*scipy.array(img.histogram())
            
            
        if img.mode=='RGB':
            pen=QtGui.QPen()
            pen.setStyle(QtCore.Qt.DotLine)
            colors=(QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.blue)
            data=(h[0:256], h[256:512], h[512:768])
            for c,  Y, col in zip((c1, c2, c3), data, colors):
                pen.setColor(col)
                c.setPen(pen)
                if Y.max()>0:
                    Y/=1.0*Y.max()
                    c.setData(X, Y)
                else:
                    c.setData([], [])
        else:
            pen=QtGui.QPen()
            pen.setStyle(QtCore.Qt.SolidLine)
            pen.setColor(QtCore.Qt.darkGray)
            c1.setPen(pen)
            if h.max()>0:
                c1.setData(X, h/h.max())
            else:
                c1.setData([], [])
            c2.setData([], [])
            c3.setData([], [])
        self.CurveDisplay.replot()
        

        
        
        
        
        
        
        
class FixedSignalingEllipseItem(SignalingEllipseItem):
    def __init__(self):
        SignalingEllipseItem.__init__(self)
        self.bbox=None
    def setBoundingBox(self, b):
        self.bbox=b
        
    def itemChange(self, change, value):
        if change==self.ItemPositionChange and self.bbox!=None:
            p=value.toPointF()
            if p.x()>self.bbox.right():
                p.setX(self.bbox.right())
            if p.x()<self.bbox.left():
                p.setX(self.bbox.left())
            if p.y()<self.bbox.top():
                p.setY(self.bbox.top())
            if p.y()>self.bbox.bottom():
                p.setY(self.bbox.bottom())
            pos=QtCore.QPointF(p.x(), p.y())
            return QtCore.QVariant(pos)
        return SignalingEllipseItem.itemChange(self, change, value)
