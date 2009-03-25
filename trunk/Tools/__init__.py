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
    
def getXMLAttributes(base, elementName, attibuteNames):
    element=base.elementsByTagName(elementName)
    if element.isEmpty():
        return
    element=element.item(0)
    if not element.isElement():
        return
    element=element.toElement()
    r=[]
    for an in attibuteNames:
        if element.hasAttribute(an):
            s=element.attribute(an)
            r.append(s)
        else:
            return
    return r

