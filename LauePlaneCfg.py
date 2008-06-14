from PyQt4 import QtGui
from Ui_LauePlaneCfgUI import Ui_LauePlaneCfgUI

class LauePlaneCfg(QtGui.QWidget, Ui_LauePlaneCfgUI):
    def __init__(self,  p,  parent):
        QtGui.QWidget.__init__(self,  parent)
        self.projector=p
        self.setupUi(self)
