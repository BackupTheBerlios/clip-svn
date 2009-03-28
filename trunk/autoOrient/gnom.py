from ToolBox import *
from math import *
import time
import LaueImage
import scipy
import Image
import scipy.ndimage

def saveArr(out, fname):
  h,w=out.shape
  i=Image.frombuffer('F',(w,h), out, 'raw', 'F;64NF')
  a=255.0/(i.getextrema()[1]-i.getextrema()[0])
  b=-a*i.getextrema()[0]
  i.point(lambda i:i*a+b).convert('L').save(fname)
  return i
  

inp=LaueImage.Image.open('testdata/SmTiO3_final8_cut.img')

s=255.0/inp.getextrema()[1]
inp.point(lambda i:i*s).convert('L').save('orig.png')

lala


L=LauePlaneProjector()
L.setDetSize(30,110.30,140.20)
L.setDetOffset(1.09, 0.69)


N=1000

#out=LaueImage.Image.new('F',(N,N))
out=scipy.zeros((N,N))


#sc=255.0/inp.getextrema()[1]

s=2.0*tan(radians(0.5*(180-L.TTmin())))/N

M=[0,0,10000,10000]
Tstart=time.time()
for x in range(N):
  print x
  for y in range(N):
    v=Vec3D(1, s*x-0.5*s*N, s*y-0.5*s*N)
    v.normalize()
    p,b=L.normal2det(v)
    w=False
    if b:
      ix=2.0*p.x()*L.dist()/L.width()
      iy=2.0*p.y()*L.dist()/L.height()
      M[0]=max(M[0],ix)
      M[1]=max(M[1],iy)
      M[2]=min(M[2],ix)
      M[3]=min(M[3],iy)
      if abs(ix)<1 and abs(iy)<1:
        ix=0.5*(ix+1)*inp.size[0]
        iy=0.5*(iy+1)*inp.size[1]
        pix=inp.getpixel((ix, iy))
        #out.putpixel((x, y), pix)
        out[x,y]=pix

def hough(arr, normal=True):
  out=scipy.zeros((180,sqrt(2)*N))
  for theta in range(out.shape[0]):
    print theta
    dx=sin(radians(theta))
    dy=cos(radians(theta))
    for r in range(out.shape[1]):
      d=r-0.5*(out.shape[1]-1)
      x0=0.5*(N-1)+d*dy
      y0=0.5*(N-1)-d*dx
      #print theta, r, d, x0, y0, dx, dy
      l=0
      for n in range(N):
	x=x0+n*dx
	y=y0+n*dy
	if x<0 or x>=N or y<0 or y>=N:
	  break
	out[theta,r]+=arr[x,y]
        l+=1

      for n in range(N):
	x=x0-n*dx
	y=y0-n*dy
	if x<0 or x>=N or y<0 or y>=N:
	  break
	out[theta,r]+=arr[x,y]
        l+=1
      if l>0 and normal:
        out[theta,r]/=l
  return out
	      
	      
  
K=scipy.zeros((15,15))
for i in range(15):
  for j in range(15):
    K[i,j]=exp(-1.0*((i-7.0)**2+(j-7.0)**2)/10.0) 
K/=K.sum()
 

o=scipy.ndimage.convolve(out, K)  
o=out-o
o=o.clip(0, o.max())


for x in range(N/5):
  for y in range(N/5):
    o[N/2+N/10-x, N/2+N/10-y]=out.min()



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



print time.time()-Tstart


#out.save('a.png')
