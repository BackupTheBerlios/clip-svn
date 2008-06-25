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

for s in range(10000):
    C=[]
    for n in range(2):
        C.append(rVn())
    RMat=Mat3D(rVn(),  10.0*random())
    V=[(RMat*x+rV(0.0)).normalized() for x in C]

    M=Mat3D((0, 0, 0, 0, 0, 0, 0, 0, 0))
    for c, v in zip(C, V):
        M=M+(c^v)
                
    S=Mat3D(M)
    L, R=S.svd()
    
    T=Mat3D()
    T[2, 2]=L.det()*R.det()
    BestR=L*T*R
    BestR.transpose()
    
    sco1=(RMat-BestR).sqSum()
    sco2=(M-L*S*R).sqSum()
    if sco1>1e-4 or sco2>1e-5:
        print sco1,  sco2,  L.det(),  R.det()
        break
    
    
    

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

 
