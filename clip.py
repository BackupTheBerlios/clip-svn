#!/usr/bin/python


import sys
import os.path
import math


from PyQt4 import QtCore, QtGui
from LaueImage import LaueImage
import Crystal
#import ImgTransferCurve
from ToolBox import ObjectStore
from ProjectionPlaneWidget import ProjectionPlaneWidget
from RotateCrystal import RotateCrystal

class clip(QtGui.QMainWindow):
    """An application called clip."""
      
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.appTitle = "CLIP 3 - Cologne Laue Indexation Program"
        self.setWindowTitle(self.appTitle)
        self.setBackgroundRole(QtGui.QPalette.Window)
        self.MdiArea=QtGui.QMdiArea(self)
        self.setCentralWidget(self.MdiArea)
        self.windowMapper = QtCore.QSignalMapper()
      
        self.connect(self.windowMapper, QtCore.SIGNAL('mapped(QWidget *)'), self.MdiArea.setActiveSubWindow)

        self.transferCurveMapper=QtCore.QSignalMapper()
        #self.connect(self.TransferCurveMapper,  QtCore.SIGNAL('mapped(QWidget*)'),  self.)
        
        

        self.rotateCrystal=RotateCrystal()
        w=self.MdiArea.addSubWindow(self.rotateCrystal)
        w.hide()
        self.connect(self.MdiArea, QtCore.SIGNAL('subWindowActivated(QMdiSubWindow*)'),  self.rotateCrystal.windowChanged)
        
        self.initActions()
        self.initMenu()
        self.initToolbar()
        
        self.lastOpenDir='.'
        
        self.statusBar().showMessage(self.appTitle+" ready", 2000)
        self.crystalStore=ObjectStore()
        
        #FIXME: Remove Debug Code
        w=self.slotNewCrystal()
        w.crystal.setCell(5, 5, 5, 90, 90, 90)
        self.slotNewStereoProjector()
        self.slotNewLauePlaneProjector()

        

    def initMenu(self):
        menudef = [
            ('&File',
             [('&Open Image', self.slotOpenImageFile), 
              ('New Crystal',  self.slotNewCrystal), 
              ('New Stereographic Projection',  self.slotNewStereoProjector)]),
            ('&Tools', 
             [('New TransferCurve', self.slotShowTransferCurve), 
              ('Rotate Crystal', self.rotateCrystal.show)]), 
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

        self.windowMenu=menus[2]
        self.slotUpdateWindowMenu()
        self.connect(self.windowMenu, QtCore.SIGNAL('aboutToShow()'), self.slotUpdateWindowMenu)

    def initActions(self):
        self.closeAct = QtGui.QAction("Cl&ose", self)
        self.closeAct.setShortcut("Ctrl+F4")
        self.closeAct.setStatusTip("Close the active window")
        self.connect(self.closeAct, QtCore.SIGNAL('triggered()'), self.MdiArea.closeActiveSubWindow)


 
        self.closeAllAct = QtGui.QAction("Close &All", self);
        self.closeAllAct.setStatusTip("Close all the windows");
        self.connect(self.closeAllAct, QtCore.SIGNAL('triggered()'), self.MdiArea.closeAllSubWindows)

        self.tileAct = QtGui.QAction("&Tile", self)
        self.tileAct.setStatusTip("Tile the windows");
        self.connect(self.tileAct, QtCore.SIGNAL('triggered()'), self.MdiArea.tileSubWindows);

        self.cascadeAct = QtGui.QAction("&Cascade", self)
        self.cascadeAct.setStatusTip("Cascade the windows")
        self.connect(self.cascadeAct, QtCore.SIGNAL('triggered()'), self.MdiArea.cascadeSubWindows)

        self.nextAct = QtGui.QAction("Ne&xt", self)
        self.nextAct.setStatusTip("Move the focus to the next window")
        self.connect(self.nextAct, QtCore.SIGNAL('triggered()'), self.MdiArea.activateNextSubWindow)

        self.previousAct = QtGui.QAction("Pre&vious", self)
        self.previousAct.setStatusTip("Move the focus to the previous window")
        self.connect(self.previousAct, QtCore.SIGNAL('triggered()'), self.MdiArea.activatePreviousSubWindow)
     


    def initToolbar(self):
      pass
	
    def slotShowTransferCurve(self):
        wid = ImgTransferCurve.ImgTransferCurve(self)
        wid.setWindowTitle('TransferCurve')
        self.MdiArea.addSubWindow(wid)
        wid.show()
        l=self.MdiArea.subWindowList(self.MdiArea.StackingOrder)
        l.reverse()
        for subWin in l:
            if isinstance(subWin.widget(), LaueImage):
                wid.setLaueImg(subWin.widget())
                break
        self.connect(self.transferCurveMapper,  QtCore.SIGNAL('mapped(QWidget*)'),  wid.setLaueImg)

    def slotUpdateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)


        windows = self.MdiArea.subWindowList();

        if len(windows)>0:
            self.windowMenu.addSeparator()

        for i,w in enumerate(windows):

            if i < 9:
                text = "&%i %s"%(i+1, w.windowTitle())
            else:
                text = "%i %s"%(i+1, w.windowTitle())

            action  = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(w==self.MdiArea.activeSubWindow())
            self.connect(action, QtCore.SIGNAL('triggered()'), self.windowMapper, QtCore.SLOT('map()'))
            self.windowMapper.setMapping(action, w)
     
 
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
        img=LaueImage(self,  fileName)
        img.setWindowTitle('Laue Image: %s'%os.path.split(fileName)[1])
        img.setMinimumSize(100, 100)
        w=self.MdiArea.addSubWindow(img)
        self.connect(w, QtCore.SIGNAL('aboutToActivate()'), self.transferCurveMapper, QtCore.SLOT('map()'))
        self.transferCurveMapper.setMapping(w, img)
        img.show()
      else:
        self.statusBar().showMessage("Loading aborted", 2000)
    
    def slotNewCrystal(self):
        wid = Crystal.Crystal(self)
        self.crystalStore.addObject(wid.crystal)
        self.connect(wid.crystal, QtCore.SIGNAL('rotationAxisChanged()'), self.rotateCrystal.rotAxisChanged)
        wid.setWindowTitle('Crystal')
        self.MdiArea.addSubWindow(wid)
        wid.show()
        return wid

    def slotNewStereoProjector(self):
        wid = ProjectionPlaneWidget(0, self)
        self.connect(wid, QtCore.SIGNAL('projectorAddedRotation(double)'), self.rotateCrystal.projectorAddedRotation)
        if self.crystalStore.size()>0:
            wid.projector.connectToCrystal(self.crystalStore.at(0))
        wid.setWindowTitle('Stereographic Projection')
        self.MdiArea.addSubWindow(wid)
        wid.show()
        return wid
        
    def slotNewLauePlaneProjector(self):
        wid = ProjectionPlaneWidget(1, self)
        self.connect(wid, QtCore.SIGNAL('projectorAddedRotation(double)'), self.rotateCrystal.projectorAddedRotation)

        if self.crystalStore.size()>0:
            wid.projector.connectToCrystal(self.crystalStore.at(0))
        wid.setWindowTitle('LauePlane')
        self.MdiArea.addSubWindow(wid)
        wid.show()
        return wid

def main(args):
    app=QtGui.QApplication(args)
    mainWindow = clip()
    mainWindow.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    app.exec_()



if __name__ == "__main__":
    main(sys.argv)


