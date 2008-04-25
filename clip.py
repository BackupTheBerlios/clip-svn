#!/usr/bin/python

#############################################################################
# clip - PyQT application template for KDevelop
#
# Translated from C++ qmakeapp.cpp
# (qmakeapp.cpp - Copyright (C) 1992-2002 Trolltech AS.  All rights reserved.)
#
# This file is part of an example program for Qt.  This example
# program may be used, distributed and modified without limitation.
#
#############################################################################

import sys
import os.path
import math
from PyQt4 import QtCore, QtGui

class clip(QtGui.QMainWindow):
    """An application called clip."""
      
    def __init__(self):
      QtGui.QMainWindow.__init__(self)
      self.appTitle = "CLIP 3 - Cologne Laue Indexation Program"
      self.setWindowTitle(self.appTitle)
      self.setBackgroundRole(QtGui.QPalette.Window)

      self.workspace=QtGui.QWorkspace(self)
      self.setCentralWidget(self.workspace)
      self.windowMapper = QtCore.QSignalMapper()
      self.connect(self.windowMapper, QtCore.SIGNAL('mapped(QWidget *)'), self.workspace.setActiveWindow)


      self.initActions()
      self.initMenu()
      self.initToolbar()

      self.lastOpenDir='.'

      self.statusBar().showMessage(self.appTitle+" ready", 2000)


    def initMenu(self):
        menudef = [
            ('&File',
             [('New Laue', self.slotOpenLauePane),
              ('&Open Image', self.slotOpenImageFile),
              ('&Close Image', self.slotCloseImageFile)]),
            ('&Windows',
             []),
            ('&Help',
             [('&About', self.slotAbout),
              ('About &QT', self.slotAboutQT),
              (None,),
              ('What\'s this', self.slotWhatsThis)])
            ]
        menus=[]
        for menuName, subMenu in menudef:
            menu=self.menuBar().addMenu( menuName )
            for menuOption in subMenu:
                if len(menuOption)==1:
                    menu.addSeparator()
                elif len(menuOption)==2:
                    menu.addAction(menuOption[0], menuOption[1])
                elif len(menuOption)==3:
                    act=menu.addAction(menuOption[0])
                    act.setCheckable(True)
                    act.setChecked(menuOption[2])
                    self.connect(act, QtCore.SIGNAL('toggled(bool)'), menuOption[1])
            menus.append(menu)

        self.windowMenu=menus[1]
        self.slotUpdateWindowMenu()
        self.connect(self.windowMenu, QtCore.SIGNAL('aboutToShow()'), self.slotUpdateWindowMenu)

    def initActions(self):
        self.closeAct = QtGui.QAction("Cl&ose", self)
        self.closeAct.setShortcut("Ctrl+F4")
        self.closeAct.setStatusTip("Close the active window")
        self.connect(self.closeAct, QtCore.SIGNAL('triggered()'), self.workspace.closeActiveWindow)


 
        self.closeAllAct = QtGui.QAction("Close &All", self);
        self.closeAllAct.setStatusTip("Close all the windows");
        self.connect(self.closeAllAct, QtCore.SIGNAL('triggered()'), self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction("&Tile", self)
        self.tileAct.setStatusTip("Tile the windows");
        self.connect(self.tileAct, QtCore.SIGNAL('triggered()'), self.workspace.tile);

        self.cascadeAct = QtGui.QAction("&Cascade", self)
        self.cascadeAct.setStatusTip("Cascade the windows")
        self.connect(self.cascadeAct, QtCore.SIGNAL('triggered()'), self.workspace.cascade)
        
        self.arrangeAct = QtGui.QAction("Arrange &icons", self)
        self.arrangeAct.setStatusTip("Arrange the icons")
        self.connect(self.arrangeAct, QtCore.SIGNAL('triggered()'), self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction("Ne&xt", self)
        self.nextAct.setStatusTip("Move the focus to the next window")
        self.connect(self.nextAct, QtCore.SIGNAL('triggered()'), self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction("Pre&vious", self)
        self.previousAct.setStatusTip("Move the focus to the previous window")
        self.connect(self.previousAct, QtCore.SIGNAL('triggered()'), self.workspace.activatePreviousWindow)
     


    def initToolbar(self):
      toolBar=QtGui.QToolBar(self)
      
      ag2=QtGui.QActionGroup(self)
      self.mouseMoveActions=[]
      mm=(('Zoom', 'F2', self.doMouseZoomEvent),
	  ('Move', 'F3', self.doMouseMoveEvent),
	  ('Rotate', 'F4', self.doMouseRotEvent),
	  ('Define Displacement', 'F5', self.doMouseDevAddEvent),
	  ('Move Primary Beam', 'F6', self.doMousePBMoveEvent),
	  ('Resize Primary Beam', 'F7', self.doMousePBSizeEvent))
      for name,short,meth in mm:
        act=QtGui.QAction(name, ag2)
        act.setCheckable(True)
	act.meth=meth
	act.setShortcut(QtGui.QKeySequence(short))
        toolBar.addAction(act)
	self.mouseMoveActions.append(act)
      self.mouseMoveActions[0].setChecked(True)
      self.mouseMoveMethod=self.doMouseZoomEvent
      self.connect(ag2, QtCore.SIGNAL('triggered(QAction*)'), self.updateKey2MouseMove)
      
      lab=QtGui.QLabel('Rotation axis: ', toolBar)
      combo=QtGui.QComboBox(toolBar)
      lab.setBuddy(combo)
      toolBar.addWidget(lab).setVisible(True)
      
      combo.addItem('x Axis')
      combo.addItem('y Axis')
      combo.addItem('z Axis')
      combo.addItem('Reflection')
      combo.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
      combo.setWindowTitle('Rotation axis')
      self.rotationCombo=combo
      self.connect(combo, QtCore.SIGNAL('currentIndexChanged(int)'), self.slotHandleRotationCombo)
      self.connect(combo, QtCore.SIGNAL('editTextChanged(const QString &)'), self.slotHandleRotationComboEdit)
      
      toolBar.addWidget(combo)

      self.addToolBar(QtCore.Qt.TopToolBarArea, toolBar)
      self.setMinimumSize(640,480)
	

    def slotOpenLauePane(self):
        wid = LatticeInput(self)
        wid.setWindowTitle('Laue Pane')
        self.workspace.addWindow(wid)
        wid.show()


    def slotUpdateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)


        windows = self.workspace.windowList();

        if len(windows)>0:
            self.windowMenu.addSeparator()

        for i,w in enumerate(windows):

            if i < 9:
                text = "&%i %s"%(i+1, w.windowTitle())
            else:
                text = "%i %s"%(i+1, w.windowTitle())

            action  = self.windowMenu.addAction(text)
            action.setCheckable(true)
            action.setChecked(w==self.workspace.activeWindow())
            self.connect(action, QtCore.SIGNAL('triggered()'), self.windowMapper, QtCore.SLOT('map()'))
            self.windowMapper.setMapping(action, w)
     
 



    def slotHandleRotationCombo(self, idx):
      self.rotationCombo.setEditable(idx>2)
      if idx>2:
        self.slotHandleRotationComboEdit(self.rotationCombo.currentText())
      else:
	self.rotAx=(Vec3D(1.0,0.0,0.0), Vec3D(0.0,1.0,0.0), Vec3D(0.0,0.0,1.0))[idx]

    def str2Ref(self,s):
      l=s.split()
      r=[]
      if len(l)==3:
        r=[]
        for i in range(3):
          try:
            r.append(float(l[i]))
          except:
            pass
      if len(r)==3:
	return r
      return None

    def slotHandleRotationComboEdit(self, s):
      if self.rotationCombo.currentIndex()==3:
        self.rotationCombo.setItemText(3, s)
      r=self.str2Ref(str(s))
      if r:
	self.rotAx=self.diff.reduced2Rezi(Vec3D(r[0], r[1], r[2])).normalize()
	self.rotationCombo.lineEdit().palette().setBrush(QtGui.QPalette.Base, QtGui.QPalette().base())
      else:
	self.rotationCombo.lineEdit().palette().setColor(QtGui.QPalette.Base, QtCore.Qt.red)

    def getAxis(self):
      idx=self.rotationCombo.currentIndex()
      if idx>2:
        r=self.str2Ref(str(self.rotationCombo.currentText()))
        if r:
	  return self.diff.reduced2Rezi(Vec3D(r[0], r[1], r[2])).normalize()
	else:
	  return Vec3D(0.0, 0.0, 0.0)
      else:
	return (Vec3D(1.0,0.0,0.0), Vec3D(0.0,1.0,0.0), Vec3D(0.0,0.0,1.0))[idx]

    def slotWhatsThis(self):
        self.whatsThis()

    def slotAbout(self):
        QtGui.QMessageBox.about(self, self.appTitle, \
                          "This is the Cologne Laue Indexation Program (CLIP)\n" + \
                          "a program for indexing Laue exposures")

    def slotAboutQT(self):
        QtGui.QMessageBox.aboutQt(self, self.appTitle)

    def slotOpenImageFile(self):
      fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Load Laue pattern', self.lastOpenDir, 'Image Plate Files (*.img);;All Images (*.jpg *.jpeg *.bmp *.png *.tif *.tiff *.gif *.img);;All Files (*)'))
      fInfo=QtCore.QFileInfo(fileName)
      if fInfo.exists():
        self.img.load(fileName)
        self.reloadImg()
        self.imgEnh.createHistogramPix()
        if self.img.lpmm_x()!=0.0 and self.img.lpmm_y()!=0.0:
          self.detector.setDetektorSize(self.img.dimx()/self.img.lpmm_x(), self.img.dimy()/self.img.lpmm_y())
      if fInfo.dir().exists():
          self.lastOpenDir=fInfo.absolutePath()
      else:
        self.statusBar().showMessage("Loading aborted", 2000)

    def slotCloseImageFile(self):
      self.img.close()
      self.reloadImg()
      self.imgEnh.createHistogramPix()
  
    def reloadImg(self):
      self.laue.img2bg()
      self.laue.update()

    def keyPressEvent(self, e):
      self.keyVal=int(e.modifiers())
      if self.modifier2MouseAction.has_key(self.keyVal):
        self.mouseMoveActions[self.modifier2MouseAction[self.keyVal]].setChecked(True)

    def keyReleaseEvent(self, e):
      self.keyVal=int(e.modifiers())
      if self.modifier2MouseAction.has_key(self.keyVal):
        self.mouseMoveActions[self.modifier2MouseAction[self.keyVal]].setChecked(True)
	
    def updateKey2MouseMove(self, act):
      self.mouseMoveMethod=act.meth
      for nr, act in enumerate(self.mouseMoveActions):
	if act.isChecked():
	  self.modifier2MouseAction[self.keyVal]=nr
	
    def slotSelectRotation(self):
      x,y=self.laue.widget2det(self.mousePressStart.x(), self.mousePressStart.y())
      idx=self.laue.closestReflex(x,y)
      if idx>=0:
	r=self.diff.getProjectedReflex(idx)
        #self.axSel.setAxis(True, r.h, r.k, r.l)
	self.rotationCombo.setCurrentIndex(3)
	self.rotationCombo.setItemText(3, '%i %i %i'%(r.h, r.k, r.l))
	
    def mousePressEvent(self, e):
      if self.laue.underMouse():
        self.mouseMode=e.buttons()
        self.modifierMode=e.modifiers()
        self.mousePressStart=self.laue.mapFromGlobal(e.globalPos())
        self.mouseActual=self.laue.mapFromGlobal(e.globalPos())
        if self.mouseMode==QtCore.Qt.RightButton and self.modifierMode==QtCore.Qt.NoModifier:
          p=QtGui.QMenu(self)
          undoZommAction=p.addAction("Undo Zoom", self.laue.slotUndoZoom)
          p.addAction("Set Rotation", self.slotSelectRotation)
	  
	  for act in self.mouseMoveActions:
	    p.addAction(act)
          p.popup(e.globalPos()-QtCore.QPoint(10,10), undoZommAction)
        else:
	  self.mouseMoveEvent(e)
	
    def mouseMoveEvent(self, e):
      if self.laue.underMouse():
	p=self.laue.mapFromGlobal(e.globalPos())
        self.mouseMoveMethod(p)
        self.mouseActual=self.laue.mapFromGlobal(e.globalPos())
        
    def mouseReleaseEvent(self, e):
      if self.laue.underMouse():
	p=self.laue.mapFromGlobal(e.globalPos())
	if abs(p.x()-self.mousePressStart.x())<5 and abs(p.y()-self.mousePressStart.y())<5:
	  if self.infoAction.isChecked():
	    x,y=self.laue.widget2det(p.x(),p.y())
	    self.laue.showPositionInfo(x,y)
	  elif self.zoneAction.isChecked():
	    x,y=self.laue.widget2img(p.x(),p.y())
            self.zoneChooser.addPoint(x,y)
	else:
          if self.mouseMoveActions[0].isChecked():
            self.laue.storeZoom()
      self.laue.setZoomRect(None)
      
    def doMouseZoomEvent(self, p):
      # ZOOM
      r=QtCore.QRect(self.mousePressStart, p)
      r=r.normalized()
      self.laue.setZoomRect(r)
      
    def doMousePBMoveEvent(self, p):
      # MOVE PRIMARY BEAM
      u=self.laue.widget2det(p.x(), p.y())
      v=self.laue.widget2det(self.mouseActual.x(), self.mouseActual.y())
      vals=self.detector.values()
      vals[6]+=(u[0]-v[0])*vals[0]
      vals[7]-=(u[1]-v[1])*vals[0]
      self.detector.setParams(vals)
    
    def doMouseRotEvent(self, p):
      # ROTATION
      u=self.diff.det2RSpace(self.laue.widget2det(p.x(), p.y()))
      v=self.diff.det2RSpace(self.laue.widget2det(self.mouseActual.x(), self.mouseActual.y()))
      #ax=self.axSel.getAxis()
      ax=self.getAxis()
      if not ax.isNull():
	u-=ax*(ax*u)
	v-=ax*(ax*v)
	u.normalize()
	v.normalize()
	a=math.acos(u*v)
	if ax*(u%v)>0:
	  a=-a
	self.diff.addRotation(ax, a)
    
    def doMouseMoveEvent(self, p):
      # MOVE
      u=self.diff.det2RSpace(self.laue.widget2det(p.x(), p.y()))
      v=self.diff.det2RSpace(self.laue.widget2det(self.mouseActual.x(), self.mouseActual.y()))
      w=v%u
      w.normalize()
      if not w.isNull():
	a=math.acos(u*v)
	self.diff.addRotation(w, a)
    
    def doMousePBSizeEvent(self, p):
      # PRIMARY BEAM RADIUS
      u=self.laue.widget2det(p.x(), p.y())
      v=self.diff.rSpace2Det(Vec3D(0.0,0.0,1.0))
      if v:
	self.laue.primBeamRadius=math.hypot(u[0]-v[0],u[1]-v[1])
	self.laue.update()
	
    def doMouseDevAddEvent(self, p):
      # DEVIATION VECTOR
      t=self.mousePressStart
      x,y=self.laue.widget2det(t.x(), t.y())
      idx=self.laue.closestReflex(x,y)
      x,y=self.laue.widget2img(p.x(), p.y())
      if idx>=0:
	ref=self.diff.getProjectedReflex(idx)
	self.emit(QtCore.SIGNAL('deviation'), (ref.h, ref.k, ref.l),(x,y))

      
def main(args):
    app=QtGui.QApplication(args)
    mainWindow = clip()
    mainWindow.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    app.exec_()



if __name__ == "__main__":
    main(sys.argv)
