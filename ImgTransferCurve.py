from Ui_ImgTransferCurve import Ui_ImgTransferCurve
from PyQt4 import QtCore, QtGui
import bisect
import sys
sys.path.append('Tools')
from BezierCurve import BezierCurve
from copy import deepcopy
from Tools import Icons
from ToolBox import SignalingEllipseItem

class ImgTransferCurve(QtGui.QWidget, Ui_ImgTransferCurve):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.connect(self.ColorSelector,  QtCore.SIGNAL('activated(int)'),  self.colorSelChanged)
        
        # Bezier Curves setup
        self.BezierParams=[]
        for i in range(4):
            self.BezierParams.append(([0, 1], [0, 1]))
                                
        # PlotDisplay Setup
        self.gs=QtGui.QGraphicsScene()
        self.gs.setSceneRect(0, 0, 1, 1)
        self.gv.setScene(self.gs)
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

        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.fileopen)), 'Load Curve')
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.filesave)), 'Save Curve')
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.flip_horizontal)), 'Flip Horizontal')
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.flip_vertikal)), 'Flip Vertical')
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.rotate_left)), 'Rotate Left')
        a=self.toolBar.addAction(QtGui.QIcon(QtGui.QPixmap(Icons.rotate_right)), 'Rotate Right')

        self.transferCurves=[]
        
        for i, c in enumerate([QtCore.Qt.black, QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.blue]):
            tc=self.gs.addPath(QtGui.QPainterPath())
            p=QtGui.QPen(c)
            p.setCosmetic(True)
            tc.setPen(p)
            self.transferCurves.append(tc)
            self.updateTransferCurve(i)
            
        self.transferCurveMarkers=[]
        
        self.renewTransferCurveMarkers()
        QtCore.QTimer.singleShot(0, self.doResize)
        
    
    def updateTransferCurve(self, idx):
        X, Y=self.BezierParams[idx]
        curve=BezierCurve(X, Y)
        path=QtGui.QPainterPath(QtCore.QPointF(X[0], Y[0]))
        for i in range(1, 51):
          x=0.02*i
          y=curve(x)
          path.lineTo(x, y)
        self.transferCurves[idx].setPath(path)
        
    def renewTransferCurveMarkers(self):
        for m in self.transferCurveMarkers:
            self.gs.removeItem(m)
        self.transferCurveMarkers=[]
        
        idx=self.ColorSelector.currentIndex()
        X, Y=self.BezierParams[idx]
        N=len(X)
        for n, x, y in zip(range(N), X, Y):
            m=FixedSignalingEllipseItem()
            m.setRect(-5, -5, 10, 10)
            m.setPos(x, y)
            if n in (0, N-1):
                m.setBoundingBox(QtCore.QRectF(x, 0, 0, 1))
                m.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))            
            else:
                m.setBoundingBox(self.gs.sceneRect())
                m.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))            
            m.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
            m.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations, True)
            
            self.gs.addItem(m)
            self.transferCurveMarkers.append(m)
            self.connect(m, QtCore.SIGNAL('positionChanged()'), self.markerMoved)
        
    def markerMoved(self):
        idx=self.ColorSelector.currentIndex()
        self.transferCurveMarkers.sort(lambda x, y:cmp(x.pos().x(), y.pos().x()))
        X=[]
        Y=[]
        for m in self.transferCurveMarkers:
            X.append(m.pos().x())
            Y.append(m.pos().y())
        self.BezierParams[idx]=(X, Y)
        self.updateTransferCurve(idx)
        
    def resizeEvent(self, e):
        self.doResize()
        
    def doResize(self):
        self.gv.fitInView(0, 0, 1, 1)
        #self.makeScales()


    def mousePressEvent(self,  e):
        p=self.gv.mapFromParent(e.pos())
        if self.rect().contains(p):
            p=self.gv.mapToScene(p)
            idx=self.ColorSelector.currentIndex()
            X, Y=self.BezierParams[idx]
            for i in range(len(X)-1):
                if p.x()>X[i] and p.x()<X[i+1]:
                    X.insert(i+1, p.x())
                    Y.insert(i+1, p.y())
                    break
            self.BezierParams[idx]=(X, Y)
            self.renewTransferCurveMarkers()
            self.updateTransferCurve(idx)
            
    def colorSelChanged(self,  i):
        self.renewTransferCurveMarkers()


        
    def makeScales(self):
        pix=QtGui.QPixmap(self.verticalScale.size())
        p=QtGui.QPainter()
        p.begin(pix)
        h=float(self.verticalScale.height())

        V=self.bezierCurves[0](scipy.arange(h)/(h-1)).clip(0, 1)
        R=255.0*self.bezierCurves[1](V).clip(0, 1)
        G=255.0*self.bezierCurves[2](V).clip(0, 1)
        B=255.0*self.bezierCurves[3](V).clip(0, 1)
        V=255.0*V
        
        for i, (v, r, g, b) in enumerate(zip(V, R, G,  B)):
            i=len(V)-i-1
            
            p.setPen(QtGui.QColor(r, g, b))
            p.drawLine(0, i, self.verticalScale.width()/2, i)
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
        
    def setLaueImg(self,  img):
        self.VRGB_BezierParams=deepcopy(img.VRGB_BezierParams)

        #self.disconnect(self)
        if self.img:
            QtCore.QObject.disconnect(self, QtCore.SIGNAL('destroyed()'), self.img.setTransferCurves)
        self.img=img
        self.connect(self, QtCore.SIGNAL('curveUpdated'), img.setTransferCurves)
        self.makeHistogram(img.fullImg)
        self.updateAllCurves()
        self.CurveDisplay.replot()
        self.makeScales()
        self.connect(img,  QtCore.SIGNAL('destroyed()'),  self.clearCurvedata)
    
    def clearCurvedata(self):
        for c in self.histogramCurves:
            c.setData([], [])
        self.img=None
        
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
