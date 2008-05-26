import sys
sys.path.append('..')

from ToolBox import Mat3D, Vec3D
from random import random

def r(d):
    return d-2*d*random()
    
def rV(d):
    return Vec3D(r(d),  r(d),  r(d))

def rVn(d=1):
    return rV(d).normalized()

C=[]
for n in range(30):
    C.append(rVn())


RMat=Mat3D(rVn(),  random())

V=[(RMat*x+rV(0.01)).normalized() for x in C]

#V[4]=rVn()

for i in range(1000):
    M1=Mat3D((0, 0, 0, 0, 0, 0, 0, 0, 0))
    M2=Mat3D((0, 0, 0, 0, 0, 0, 0, 0, 0))

    for c, v in zip(C, V):
        for i in range(3):
            for j in range(3):
                M1[i, j]+=c[i]*c[j]
                M2[i, j]+=v[i]*c[j]
            
    M=M2*M1.inverse()
    score=[]
    for i in range(10):
        
        score.append(sum([(v-T*c).norm() for c, v in zip(C, V)]))
        M=M.orthogonalize()
