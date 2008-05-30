from scipy.linalg import svd
from scipy import zeros
from ToolBox import Vec3D,  Mat3D

class Solution:
    pass
    
class SolutionFinder:
    pass
    



def bestRotMatrix(Varr1,  Varr2):
    M=zeros((3, 3))
    for c, v in zip(Varr1,  Varr2):
        for i in range(3):
            for j in range(3):
                M[i, j]+=c[i]*v[j]
                
    U, s, V=scipy.linalg.svd(M)
    U=Mat3D(U)
    V=Mat3D(V)
    I=Mat3D()
    I[2,2]=U.det()*V.det()
    return V*I*U
    
def gcd(a,b):
  while b!=0:
    (a,b)=(b,a%b)
  return abs(a)
    
def gcdl(*arg):
  if len(arg)==1:
    #Arg is a list
    arg=arg[0]
  return reduce(gcd, arg)

def nrange(N):
    yield 0
    n=1
    while n<=N:
        yield -n
        yield n
        n+=1

def genHkl(n,full=False):
    R=[]
    if full:
      check=lambda h,k,l: not (h==0 and k==0 and l==0)
    else:
      check=lambda h,k,l:gcdl(h,k,l)==1
    for h in range(0, n+1):
        for k in range(0, n+1):
            if abs(h)==n or abs(k)==n:
                Ra=range(-n, n+1)
            else:
                Ra=(-n, n)
            for l in Ra:
                if check(h,k,l):
                    R.append((h, k, l))
    return R

def indexUnit(v):
    m=reduce(max, [abs(v[i]) for i in (0,1,2)])
    # PARAM max maxIndex
    for n in range(1, 15):
        vt=v*n/m
        alpha=sum([round(vt[i])*v[i] for i in (0,1,2)])
        s=0
        r=[]
        for i in (0, 1, 2):
            t=alpha*v[i]
            tr=int(round(t))
            s+=abs(t-tr)
            r.append(tr)
        # PARAM summedHKL deviation
        if s<0.2:
            return tuple(r)
    return None


def solutionScore(s):
  S=[(OMat*Vec3D(x)).normalized() for x in s]
  R=bestRotMatrix(V,S)
  score=sum([(a-R*b).norm_sq() for a,b in zip(S,V)])
  return score,R
  
  

def calcSolution(R):
    SolIdx=[]
    for n, v in enumerate(V):
        vr=(R*v).normalized()
        hkl=indexUnit(vr)
        if hkl==None:
            return None
        else:
            SolIdx.append(hkl)
    return tuple(SolIdx)
    
def do():
    Chkl=genHkl(1)+genHkl(2)+genHkl(3)
    
    C=[(OMat*Vec3D(x)).normalized() for x in Chkl]
    
    RMat=Mat3D(Vec3D(0.5-random(),  0.5-random(),  0.5-random()).normalized(),  3.14*random())
    
    Vidx=[randint(0,  len(Chkl)-1) for x in range(6)]
    V=[(RMat*C[i]+rV(0.01)).normalized() for i in Vidx]

    realSolution=tuple([Chkl[i] for i in Vidx])
    
    Vang=[]
    
    for i in range(len(V)):
        for j in range(i):
            #Vang.append((i, j, math.acos(V[i]*V[j])))
            ang=max(-1,min(1,V[i]*V[j]))
            # PARAM angular mismatch
            dang=abs(math.cos(math.acos(ang)+0.01)-ang)
            Vang.append((i, j, ang,dang))
    
    
    
    NAngMatch=0
    solutions=[]
    print "newSearch"
    for i in range(len(C)):
        for j in range(i):
            Cang=C[i]*C[j]
            for u, v, a, da in Vang:
                if abs(Cang-a)<da:
                    NAngMatch+=1
                    for Va in ((V[u],  V[v]),  (V[v],  V[u])):
                        Rcand=bestRotMatrix(Va,  (C[i],  C[j]))
                        SolIdx=calcSolution(OMat.inverse()*Rcand)
                        if SolIdx!=None:
                            newSol=True
                            for s in solutions:
                              if s[1]==SolIdx:
                                newSol=False
                                break
                            if newSol:
                                solutions.append((Rcand,  SolIdx))
    ok=0
    for n,s in enumerate(solutions):
      if s[1]==realSolution:
        print "realsolution at",n
        ok+=1
    if ok!=1:
      print " realSolution not found?"
      #break
