import sys
sys.path.append('..')
from scipy.linalg import svd
from scipy import zeros
from ToolBox import Vec3D,  Mat3D
from Queue import Queue,  Empty
from threading import Thread
import time
import math

class Solution:
    def __init__(self, indexRotation,  OMat,  OMatInv):
        self.OMat=OMat
        self.OMatInv=OMatInv
        self.indexRotation=indexRotation
        self.HKLs=[]
        self.alphas=[]
        self.indexedVectors=[]
        self.HKLVectors=None
        self.bestRotation=None
        self.score=None
        self.angularDeviation=None

    def addHkl(self,  hkl,  v,  alpha):
        self.HKLs.append(hkl)
        self.indexedVectors.append(v)
        self.alphas.append(alpha)
        self.HKLVectors=None
        self.bestRotation=None
        self.score=None
        self.angularDeviation=None
        
    def calcBestRotation(self):
        self.HKLVectors=[(self.OMat*Vec3D(x)).normalized() for x in self.HKLs]
        self.bestRotation=bestRotMatrix(self.indexedVectors,  self.HKLVectors)
        
    def calcSolutionScore(self):
        if self.HKLVectors==None or self.bestRotation==None:
            self.calcBestRotation()
        self.score=sum([(a-self.bestRotation*b).norm_sq() for a,b in zip(self.HKLVectors,  self.indexedVectors)])
        
    def calcAngularDeviation(self):
        if self.HKLVectors==None or self.bestRotation==None:
            self.calcBestRotation()
        self.angularDev=math.degrees(sum([abs(math.acos(a*(self.bestRotation*b))) for a,b in zip(self.HKLVectors,  self.indexedVectors)]))
        
        
    def calcRealHKL(self):
        if self.HKLVectors==None or self.bestRotation==None:
            self.calcBestRotation()
        vs=[(self.OMatInv*self.bestRotation*iv).normalized()*alpha for iv, alpha in zip(self.indexedVectors,  self.alphas)]
        return [(v[0],  v[1],  v[2]) for v in vs]

    def solutionScore(self):
        if self.score==None:
            self.calcSolutionScore()
        return self.score

    def angularDeviation(self):
        if self.angularDev==None:
            self.calcAngularDeviation()
        return self.angularDev
  
        
        
class SolutionFinder:
    def __init__(self):
        self.OMat=None
        self.OMatInv=None
        self.V=None
        self.maxAngularDev=math.radians(2.0)
        self.maxTriedIndex=25
        self.maxDeviationFromInt=0.05
        
        self.workers=[]
        for i in range(1):
            w=Thread(target=self.worker, args=[i])
            w.setDaemon(True)
            w.start()
            self.workers.append(w)
        self.solutions=[]
        self.workQueue=Queue(0)
        self.solutionQueue=Queue(0)
        
    def worker(self, workerNr):
        while True:
            i, j=self.workQueue.get()
            #print 'Worker ',workerNr,':', i, j
            C1=self.Candidates[i]
            C2=self.Candidates[j]
            Cang=C1*C2
            
            for u, v, a, da in self.Vang:
                if abs(Cang-a)<da:
                    for k, l in ((u, v), (v, u)):
                        V1=self.V[k]
                        V2=self.V[l]
                        Rcand=bestRotMatrix((V1,  V2),  (C1,  C2))
                        R=self.OMatInv*Rcand
                        s=Solution(Rcand,  self.OMat,  self.OMatInv)
                        for n, v in enumerate(self.V):
                            vr=(R*v).normalized()
                            hkl=self.indexUnitvector(vr,  Hint=1)
                            if hkl==None:
                                break
                            else:
                                s.addHkl(hkl[0],  v,  hkl[1])
                        else:
                            self.solutionQueue.put(s)
            self.workQueue.task_done()

    def startWork(self):
        print ' Clear the Working Queue'
        ok=True
        while ok:
            try:
                self.workQueue.get_nowait()
                self.workQueue.task_done()
            except Empty:
                ok=False
        
        print 'Wait for workers to finish'
        self.workQueue.join()


        print 'Creating candidates'
        self.Candidates=[(self.OMat*Vec3D(hkl)).normalized() for hkl in genHkl(1)+genHkl(2)]
        self.solutions=[]
        print 'creating work'
        if self.OMat!=None and self.V!=None and self.maxAngularDev!=None and self.maxDeviationFromInt!=None and self.maxTriedIndex!=None:
            for i in range(len(self.Candidates)):
                for j in range(i):
                    self.workQueue.put((i, j))
            
    def setOMat(self,  M):
        self.OMat=M
        self.OMatInv=M.inverse()

    def setVectors(self,  V):
        self.V=V
        self.calcAngles()

    def calcAngles(self):
        if self.V!=None and self.maxAngularDev!=None:
          self.Vang=[]
          for i in range(len(self.V)):
              for j in range(i):
                  ang=max(-1,min(1,self.V[i]*self.V[j]))
                  # PARAM angular mismatch
                  dang=abs(math.cos(math.acos(ang)+self.maxAngularDev)-ang)
                  self.Vang.append((i, j, ang, dang))
 
    def setMaxAngularDeviation(self,  v):
        self.maxAngularDev=v
        
        self.calcAngles()
    
    def setMaxDeviationFromInt(self,  v):
        self.maxDeviationFromInt=v
        
    def setMaxTriedIndex(self,  v):
        self.maxTriedIndex=v
    
    def indexUnitvector(self,  v,  Hint=1):
        m=reduce(max, [abs(v[i]) for i in (0,1,2)])
        # PARAM max maxIndex
        for n in range(self.maxTriedIndex):
            nr=1.0*(((n+Hint-1)%self.maxTriedIndex)+1)
            vt=v*nr/m
            alpha=sum([round(vt[i])*v[i] for i in (0,1,2)])
            r=[]
            for i in (0, 1, 2):
                t=alpha*v[i]
                tr=int(round(t))
                if abs(t-tr)<self.maxDeviationFromInt:
                  r.append(tr)
            if len(r)==3:
              return tuple(r), alpha
        return None


    def calcSolution(self,  R):
        SolIdx=[]
        for n, v in enumerate(self.V):
            vr=(R*v).normalized()
            hkl=self.indexUnitvector(vr)
            if hkl==None:
                return None
            else:
                SolIdx.append(hkl)
        return tuple(SolIdx)






def pmrange(N):
    yield 0
    n=1
    while n<=N:
        yield n
        yield -n
        n+=1

def gcd(a,b):
  while b!=0:
    (a,b)=(b,a%b)
  return abs(a)
    
def gcdl(*arg):
  if len(arg)==1:
    #Arg is a list
    arg=arg[0]
  return reduce(gcd, arg)

def genHkl(n,full=False):
    R=[]
    if full:
      check=lambda h,k,l: not (h==0 and k==0 and l==0)
    else:
      check=lambda h,k,l:gcdl(h,k,l)==1
    for h in pmrange(n):
        for k in pmrange(n):
            if abs(h)==n or abs(k)==n:
                Ra=pmrange(n)
            else:
                Ra=(-n, n)
            for l in Ra:
                if check(h,k,l):
                    R.append((h, k, l))
    return R



def bestRotMatrix(Varr1,  Varr2):
    M=zeros((3, 3))
    for c, v in zip(Varr1,  Varr2):
        for i in range(3):
            for j in range(3):
                M[i, j]+=c[i]*v[j]
                
    U, s, V=svd(M)
    U=Mat3D(U)
    V=Mat3D(V)
    I=Mat3D()
    I[2,2]=U.det()*V.det()
    return V*I*U
    






  

def rV(d):
  from random import randint,random
  return Vec3D(d-2.0*d*random(),d-2.0*d*random(),d-2.0*d*random())


def do(s):
    from random import randint,random
    OMat = Mat3D()
    OMat[0,0]=5.317
    OMat[1,1]=5.563

    OMat[2,2]=19.7234
    RMat=Mat3D(Vec3D(0.5-random(),  0.5-random(),  0.5-random()).normalized(),  3.14*random())
    
    Vhkl=[(randint(-i,i), randint(-i,i), randint(-i,i)) for i in (2,2,9,9,9,9,9,9)]
      
    V=[(RMat*OMat*(Vec3D(hkl)+rV(0.001))).normalized() for hkl in Vhkl]

    s.setVectors(V)
    s.setOMat(OMat)
    
    
    return RMat, OMat, Vhkl, V
