import sys
import scipy
import scipy.linalg

sys.path.append('..')

from ToolBox import Mat3D, Vec3D
from random import random

def r(d):
    return d-2*d*random()
    
def rV(d):
    return Vec3D(r(d),  r(d),  r(d))

def rVn(d=1):
    return rV(d).normalized()

    
def outer(v):
  M=Mat3D()
  for i in range(3):
    for j in range(3):
      M[i,j]=v[i]*v[j]
  return(M)

for s in range(10):
    C=[]
    for n in range(10):
        C.append(rVn())
    RMat=Mat3D(rVn(),  3*random())
    V=[(RMat*x+rV(0.1)).normalized() for x in C]
    #V=[RMat*x for x in C]

    M=scipy.zeros((3, 3))
    for c, v in zip(C, V):
        for i in range(3):
            for j in range(3):
                M[i, j]+=c[i]*v[j]
                
    U, s, V=scipy.linalg.svd(M)
    M=Mat3D(M)
    U=Mat3D(U)
    V=Mat3D(V)
    S=Mat3D()
    for i in range(3):
        S[i, i]=s[i]
    
    sco=(RMat-V*U).sqSum()
    print (M-V*S*U).sqSum(), sco
    
    

def UToUpper(M):
    v1=M*Vec3D(1,0,0)
    u1=v1-Vec3D(1,0,0)*v1.norm()
    u1.normalize()
    R1=Mat3D()-outer(u1)*2

    v2=R1*M*Vec3D(0,1,0)
    v2[0]=0.0
    u2=v2-Vec3D(0,1,0)*v2.norm()
    u2.normalize()
    R2=Mat3D()-outer(u2)*2
    return R2*R1
    
def LRToBiDiag(M):
    v1=M*Vec3D(1,0,0)
    u1=(v1-Vec3D(1,0,0)*v1.norm()).normalized()
    L1=Mat3D()-outer(u1)*2
    
    v2=(L1*M).transpose()*Vec3D(1,0,0)
    v2[0]=0
    u2=(v2-Vec3D(0,1,0)*v2.norm()).normalized()
    R=(Mat3D()-outer(u2)*2).transpose()
    

    v3=L1*M*R*Vec3D(0,1,0)
    v3[0]=0.0
    u3=(v3-Vec3D(0,1,0)*v3.norm()).normalized()
    L2=Mat3D()-outer(u3)*2
    return L2*L1, R

 
