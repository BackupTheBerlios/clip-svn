import sys
sys.path.append('..')

from ToolBox import *
from math import *
import time
import LaueImage
from scipy import arange, linspace, fromstring,  float64, float32, zeros
import Image
import scipy.ndimage
import scipy.interpolate
import random

def Img(arr):
    h, w=arr.shape
    if arr.dtype==float64:
        S='F;64NF'
    else:
        S='F;32NF'
        
    i=Image.frombuffer('F',(w,h), arr, 'raw', S)
    a=255.0/(i.getextrema()[1]-i.getextrema()[0])
    b=-a*i.getextrema()[0]
    return i.point(lambda i:i*a+b).convert('L')




def genBG(img, mask):
    x=[]
    y=[]
    z=[]
    w=[]
    
    #while len(x)<500:
    #    i=random.randrange(img.shape[0])
    #    j=random.randrange(img.shape[1])
     
    for i in linspace(0, img.shape[0]-1, 20): 
      for j in linspace(0, img.shape[1]-1, 20): 
        i=int(i)
        j=int(j)
        
        if mask!=None and mask[i, j]==0.0:
            continue
        a=img[max(0, i-10):i+10, max(0, j-10):j+10]
        #print sqrt(a.sum()), a.std()
        
        x.append(1.0*i)
        y.append(1.0*j)
        z.append(img[i, j])
        w.append(1.0/a.std())
        
    
    
    s=scipy.interpolate.bisplrep(x, y, z, w=w, xb=0,  xe=img.shape[0], yb=0, ye=img.shape[1], s=1e3)
    BG=scipy.interpolate.bisplev(arange(img.shape[0]), arange(img.shape[1]), s)
    
    return BG



def gnom(img, L):
    out=zeros((N,N))
    mask=zeros((N,N))
    
    s=2.0*tan(radians(0.5*(180-L.TTmin())))/N
    
    for x in range(N):
      print x
      for y in range(N):
        v=Vec3D(1, s*x-0.5*s*N, s*y-0.5*s*N)
        v.normalize()
        if v[0]>cos(radians(6.0)):
            continue
        p,b=L.normal2det(v)
        if b:
          ix=2.0*p.x()*L.dist()/L.width()
          iy=2.0*p.y()*L.dist()/L.height()
          if abs(ix)<1 and abs(iy)<1:
            ix=0.5*(ix+1)*img.shape[0]
            iy=0.5*(iy+1)*img.shape[1]
            out[x,y]=img[ix, iy]
            mask[x, y]=1.0
            
    return out, mask







inp=LaueImage.Image.open('../testdata/SmTiO3_final8_cut.img')

T=time.time()
img=fromstring(inp.tostring(), dtype=float32)
img=img.reshape((inp.size[1], inp.size[0]))
print "convert:", time.time()-T

L=LauePlaneProjector()
L.setDetSize(30,140.20,110.30)
L.setDetOffset(1.09, 0.69)


N=200

gn, mask=gnom(img, L)
BG=genBG(gn, mask)

a=gn-BG*mask


def hough(arr, normal=True,  ang=None, R=None):
  if ang==None:
    ang=range(180)
  if R==None:
    R=range(-sqrt(0.5)*N, sqrt(0.5)*N)
 
  out=zeros((len(ang), len(R)))
  for i, theta in enumerate(ang):
    print theta
    dx=sin(radians(theta))
    dy=cos(radians(theta))
    for j, d in enumerate(R):
      x0=0.5*(N-1)+d*dy
      y0=0.5*(N-1)-d*dx
      #print theta, r, d, x0, y0, dx, dy
      l=0
      for n in range(N):
	x=x0+n*dx
	y=y0+n*dy
	if x<0 or x>=N or y<0 or y>=N:
	  break
	out[i, j]+=arr[x,y]
        l+=1

      for n in range(N):
	x=x0-n*dx
	y=y0-n*dy
	if x<0 or x>=N or y<0 or y>=N:
	  break
	out[i, j]+=arr[x,y]
        l+=1
      if l>0 and normal:
        out[i, j]/=l
  return out
	      
	      
  



#h=hough(o, False)

def markLine(out, h):
  idx=h.argmax()
  theta=idx/h.shape[1]
  r=idx%h.shape[1]
  print "Max@ ",theta,r

  for x in range(-4,5):
    for y in range(-4,5):
      try:
        h[theta+x,r+y]=h.min()
      except:
        pass

  dx=sin(radians(theta))
  dy=cos(radians(theta))
  d=r-0.5*(h.shape[1]-1)

  x0=0.5*(N-1)+d*dy
  y0=0.5*(N-1)-d*dx
  for n in range(N):
    x=x0+n*dx
    y=y0+n*dy
    if x<0 or x>=N or y<0 or y>=N:
       break
    out[x,y]=out.max()
  return out


