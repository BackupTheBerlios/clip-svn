from ToolBox import Vec3D, Mat3D
import math

def calcAngles(v1,  v2,  phi,  chi):
    u1, u2=calcLine(v1, v2, phi, chi)
    intermediates=calcIntermediates(u1, u2)
    
    if intermediates==None:
        return None
    
    r=[]
    for c in intermediates:
        aChi=calcRotationAngle(v1, c, chi)
        aPhi=calcRotationAngle(c, v2, phi)
        r.append((aPhi, aChi))
    r.sort(lambda x, y:cmp(abs(x[0])+abs(x[1]),  abs(y[0])+abs(y[1])))
    return r

def calcLine(v1,  v2,  phi,  chi):
    u2=phi%chi
    u2.normalize()
    
    pc=phi*chi
    denom=1.0-pc**2
    if denom<=0.0:
        return None
        
    t1=v1*chi
    t2=v2*phi
    
    lam=(t2-pc*t1)/denom
    mu=(t1-pc*t2)/denom
    
    return phi*lam+chi*mu, u2
    
def calcIntermediates(u1, u2):
    l=u1.norm_sq()
    if l>1.0:
        return None
    elif l==1.0:
        return (u1, )
    else:
        l=math.sqrt(1.0-l)
        return (u1+u2*l, u1-u2*l)
    
def calcRotationAngle(fromV,  toV,  axis):
    v1=fromV-axis*(fromV*axis)
    v1.normalize()
    
    v2=toV-axis*(toV*axis)
    v2.normalize()
    
    M=Mat3D(fromV, toV, axis)
    if M.det()<0:
        return -math.acos(v1*v2)
    else:
        return math.acos(v1*v2)
