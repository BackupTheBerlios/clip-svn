import scipy
import bisect
import numpy

class BezierCurve:
    ''' Calculates a Bezier Spline, like in the Color-Curve-Dialog in Gimp
        The Cubic Bezier-Curve is: y=P0*(1-t)**3+3*P1*(1-t)**2*t+3*P2*(1-t)*t**2+P3*t**3
        This gives with t=(x - x_i)/(x_i+1 - x_i), dx=x - x_i, D=x_i+1 - x_i
        C0=P0
        C1=(3*P1-3*P0)/D
        C2=(3*P3-6*P1+3*P0)/D**2        
        C3=(P3-3*P2+3*P1-P0)/D**3
        
        y=(((C3*dx)+C2)*dx+C1)*dx+C0
        
        and again with
        
        D0=C0 - C1*x_i + C2*x_i**2 - C3*x_i**3
        D1=C1 -2*C2*x_i + 3*C3*x_i**2
        D2=C2 - 3*C3*x_i
        D3=C3
        
        y=(((D3*x)+D2)*x+D1)*x+D0
    '''
    def __init__(self,  x,  y):
        # this ist stolen from GIMP. Hale the GPL!!!
        # File: GIMP/app/base/curves.c
        self.x=x
        if len(x)<2:
            raise ValueError,  'need minimal 2 Points'
        elif len(x)==2:
            self.P=[(y[0],  y[0]+(y[1]-y[0])/3.0,  y[0]+2.0*(y[1]-y[0])/3.0,  y[1])]
            self.C=[(y[0],  (y[1]-y[0])/(x[1]-x[0]),  0.0,  0.0)]
            self.D=[((y[0]-(y[1]-y[0])/(x[1]-x[0])*x[0]),  (y[1]-y[0])/(x[1]-x[0]),  0.0,  0.0)]
        else:
            self.P=[]
            self.C=[]
            self.D=[]
            for i in range(len(x)-1):
                P0=y[i]
                P3=y[i+1]
                dx=x[i+1]-x[i]
                if i==0:
                    #only the right neighbor is available. Make the tangent at the
                    #right endpoint parallel to the line between the left endpoint
                    #and the right neighbor. Then point the tangent at the left towards
                    #the control handle of the right tangent, to ensure that the curve
                    #does not have an inflection point.
                    slope = (y[i+2] - y[i]) / (x[i+2] - x[i]);
                    P2 = y[i+1] - slope * dx / 3.0;
                    P1 = y[i] + (P2 - y[i]) / 2.0;
                elif i==len(x)-2:
                    slope = (y[i+1] - y[i-1]) / (x[i+1] - x[i-1]);
                    P1 = y[i] + slope * dx / 3.0;
                    P2 = y[i+1] + (P1 - y[i+1]) / 2.0;
                else:
                    # Both neighbors are available. Make the tangents at the endpoints
                    # parallel to the line between the opposite endpoint and the adjacent
                    #neighbor.
                    slope = (y[i+1] - y[i-1]) / (x[i+1] - x[i-1])
                    P1 = y[i] + slope * dx / 3.0
                    slope = (y[i+2] - y[i]) / (x[i+2] - x[i])
                    P2 = y[i+1] - slope * dx / 3.0
                self.P.append((P0,  P1,  P2,  P3))
                
                C0=P0
                C1=(        3*P1-3*P0)/dx
                C2=(   3*P2-6*P1+3*P0)/dx**2        
                C3=(P3-3*P2+3*P1-  P0)/dx**3
                self.C.append((C0, C1, C2, C3))
                
                D0=C0 -   C1*x[i] +   C2*x[i]**2 - C3*x[i]**3
                D1=C1 - 2*C2*x[i] + 3*C3*x[i]**2
                D2=C2 - 3*C3*x[i]
                D3=C3
                self.D.append((D0,  D1,  D2,  D3))

    def calcFromP(self,  x):
        n=min(max(bisect.bisect(self.x,  x)-1, 0),  len(self.x)-2)
        t=(x-self.x[n])/(self.x[n+1]-self.x[n])
        t1=1.0-t
        return self.P[n][0]*t1**3+3*self.P[n][1]*t1**2*t+3*self.P[n][2]*t1*t**2+self.P[n][3]*t**3

    def calcFromC(self,  x):
        n=min(max(bisect.bisect(self.x,  x)-1, 0),  len(self.x)-2)
        return ((self.C[n][3]*(x-self.x[n])+self.C[n][2])*(x-self.x[n])+self.C[n][1])*(x-self.x[n])+self.C[n][0]
    
    def calcFromD(self,  x):
        n=min(max(bisect.bisect(self.x,  x)-1, 0),  len(self.x)-2)
        return ((self.D[n][3]*x+self.D[n][2])*x+self.D[n][1])*x+self.D[n][0]

    def calcFromUnsortedScipyArr(self,  arr):
        sortedArr=scipy.array(arr)
        sortedArr.sort()
        nl=0
        for x,D in zip(self.x[1:],  self.D):
            D0, D1, D2, D3=D
            nr=bisect.bisect(sortedArr,  x)
            v=sortedArr[nl:nr]
            sortedArr[nl:nr]=((D3*v+D2)*v+D1)*v+D0
            nl=nr
        res=scipy.zeros(arr.shape)
        for i, n in enumerate(arr.argsort()):
            res[n]=sortedArr[i]
        return res.clip(0, 1)
        
    def __call__(self,  x):
        if type(x) in (int,  float):
            return self.calcFromP(x)
        elif type(x)==numpy.ndarray:
            return scipy.array(map(self.calcFromD,  x))
        elif hasattr(x,  '__iter__'):
            return map(self.calcFromD,  x)
