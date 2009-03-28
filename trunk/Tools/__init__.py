from PyQt4 import QtGui
from ToolBox import Vec3D

ToolBar = QtGui.QToolBar


def parseHKL(s):
    try:
        return Vec3D(map(float, s.split()))
    except:
        if len(s)==3:
            try:
                return Vec3D([float(s[i]) for i in (0, 1, 2)])
            except:
                pass
    return None
    

