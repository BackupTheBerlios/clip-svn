from Ui_ImgTransferCurveWidget import Ui_TransferCurve
from PyQt4 import QtCore, QtGui
import bisect
import scipy
import sys
sys.path.append('Tools')
import BezierCurve
from copy import deepcopy


class ImgTransferCurve(QtGui.QWidget, Ui_TransferCurve):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.connect(self.ColorSelector,  QtCore.SIGNAL('activated(int)'),  self.colorSelChanged)
        
        # Bezier Curves setup
        self.VRGB_BezierParams=[[(0, 0),  (1, 1)], 
                               [(0, 0),  (1, 1)], 
                               [(0, 0),  (1, 1)], 
                               [(0, 0),  (1, 1)]]
                               
        self.bezierCurves=[None]*4
        self.img=None
 
        # PlotDisplay Setup
        self.CurveDisplay.enableAxis(Qwt5.QwtPlot.xBottom, False)
        self.CurveDisplay.enableAxis(Qwt5.QwtPlot.yLeft, False)
        self.CurveDisplay.setAxisScale(Qwt5.QwtPlot.xBottom,  0.0,  1.0,  0.25)
        self.CurveDisplay.setAxisScale(Qwt5.QwtPlot.yLeft    ,  0.0,  1.0,  0.25)
        
        # Plot Grid setup
        self.plotGrid=Qwt5.QwtPlotGrid()
        pen=QtGui.QPen()
        pen.setStyle(QtCore.Qt.DashLine)
        pen.setColor(QtCore.Qt.gray)
        self.plotGrid.setPen(pen)
        self.plotGrid.attach(self.CurveDisplay)
        
        # Curve for the Bezier Point handles
        self.handlesCurve=Qwt5.QwtPlotCurve()
        self.handlesCurve.setSymbol(Qwt5.QwtSymbol(Qwt5.QwtSymbol.Ellipse,  QtCore.Qt.black,  QtCore.Qt.black,  QtCore.QSize(5, 5)))
        self.handlesCurve.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        
        # Curve for the Image Histogram
        self.histogramCurves=[Qwt5.QwtPlotCurve(),  Qwt5.QwtPlotCurve(),  Qwt5.QwtPlotCurve()]
        
        for c in self.histogramCurves+[self.handlesCurve]:
            c.attach(self.CurveDisplay)

        self.splineCurves=[Qwt5.QwtPlotCurve(), Qwt5.QwtPlotCurve(),  Qwt5.QwtPlotCurve(), Qwt5.QwtPlotCurve()]
        for col, curve in zip((QtCore.Qt.blue, QtCore.Qt.green, QtCore.Qt.red, QtCore.Qt.black),  self.splineCurves):
            curve.setPen(col)
            curve.attach(self.CurveDisplay)
        self.splineCurves.reverse()
        self.splineCurves=tuple(self.splineCurves)
        
        self.updateAllCurves()
        self.makeScales()

    def colorSelChanged(self,  i):
        data=zip(*self.VRGB_BezierParams[self.ColorSelector.currentIndex()])
        self.handlesCurve.setData(*data)
        self.CurveDisplay.replot()
        self.makeScales()
        
    def resizeEvent(self, e):
        self.makeScales()
        
    def updateCurves(self):
        data=zip(*self.VRGB_BezierParams[self.ColorSelector.currentIndex()])
        self.handlesCurve.setData(*data)
        self.bezierCurves[self.ColorSelector.currentIndex()]=BezierCurve.BezierCurve(*data)
        interpX=scipy.arange(0, 1.01,  0.01)
        self.splineCurves[self.ColorSelector.currentIndex()].setData(interpX,  scipy.array(self.bezierCurves[self.ColorSelector.currentIndex()](interpX)).clip(0, 1))
        #self.emit(QtCore.SIGNAL('curveUpdated'),  deepcopy(self.VRGB_BezierParams))
        if self.img:
            self.img.setTransferCurves(deepcopy(self.VRGB_BezierParams))

    def updateAllCurves(self):
        for i in range(4):
            data=zip(*self.VRGB_BezierParams[i])
            if i==self.ColorSelector.currentIndex():
                self.handlesCurve.setData(*data)
            self.bezierCurves[i]=BezierCurve.BezierCurve(*data)
            interpX=scipy.arange(0, 1.01,  0.01)
            self.splineCurves[i].setData(interpX,  scipy.array(self.bezierCurves[i](interpX)).clip(0, 1))

    def mousePressEvent(self,  e):
        if self.CurveDisplay.geometry().contains(e.pos()):
            p=self.CurveDisplay.mapFrom(self,  e.pos())
            idx,  dist=self.handlesCurve.closestPoint(p)
            if dist>10:
                x=self.CurveDisplay.invTransform(Qwt5.QwtPlot.xBottom,  p.x())
                y=self.CurveDisplay.invTransform(Qwt5.QwtPlot.yLeft,  p.y())
                self.lastInsertindex=bisect.bisect(zip(*self.VRGB_BezierParams[self.ColorSelector.currentIndex()])[0],  x)
                self.VRGB_BezierParams[self.ColorSelector.currentIndex()].insert(self.lastInsertindex,  (x,  y))
                self.updateCurves()
                self.CurveDisplay.replot()
                self.makeScales()
            else:
                self.lastInsertindex=idx
        
    def mouseMoveEvent(self,  e):
        if self.CurveDisplay.geometry().contains(e.pos()) and self.lastInsertindex!=None:
            p=self.CurveDisplay.mapFrom(self,  e.pos())
                
            x=self.CurveDisplay.invTransform(Qwt5.QwtPlot.xBottom,  p.x())
            y=max(0, min(1,  self.CurveDisplay.invTransform(Qwt5.QwtPlot.yLeft,  p.y())))
            if self.lastInsertindex==0 or self.lastInsertindex+1==len(self.VRGB_BezierParams[self.ColorSelector.currentIndex()]):
                x=self.CurveDisplay.invTransform(Qwt5.QwtPlot.xBottom,  p.x())
                self.VRGB_BezierParams[self.ColorSelector.currentIndex()][self.lastInsertindex]=(self.VRGB_BezierParams[self.ColorSelector.currentIndex()][self.lastInsertindex][0],  y)
            elif self.VRGB_BezierParams[self.ColorSelector.currentIndex()][self.lastInsertindex-1][0]<x and self.VRGB_BezierParams[self.ColorSelector.currentIndex()][self.lastInsertindex+1][0]>x:
                self.VRGB_BezierParams[self.ColorSelector.currentIndex()][self.lastInsertindex]=(x,  y)
            else:
                self.VRGB_BezierParams[self.ColorSelector.currentIndex()].pop(self.lastInsertindex)
                self.lastInsertindex=None
            self.updateCurves()
            self.makeScales()
            self.CurveDisplay.replot()

    def mouseReleaseEvent(self,  e):
        pass
        
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
