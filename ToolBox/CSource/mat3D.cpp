#include "mat3D.h"
#include <cmath>
#include <stdio.h>

Mat3D::Mat3D() {
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      M[i][j]=(i==j)?1.0:0.0;
}

Mat3D::Mat3D(const Mat3D* t) {
  memcpy(&M, &(t->M), 9*sizeof(double));
}

Mat3D::Mat3D(const Mat3D& t) {
  memcpy(&M, &(t.M), 9*sizeof(double));
}

Mat3D::Mat3D(Vec3D v1,Vec3D v2,Vec3D v3) {
  for (unsigned int i=3; i--; ) {
    M[i][0]=v1[i];
    M[i][1]=v2[i];
    M[i][2]=v3[i];
  }
}


Mat3D::Mat3D(Vec3D axis, double angle) {
  // from http://www.euclideanspace.com/maths/algebra/matrix/orthogonal/rotation/
  
  double s = sin(angle);
  double c = cos(angle);
  double x = axis[0];
  double y = axis[1];
  double z = axis[2];

  M[0][0]=1.0+(1.0-c)*(x*x-1.0);
  M[1][1]=1.0+(1.0-c)*(y*y-1.0);
  M[2][2]=1.0+(1.0-c)*(z*z-1.0);

  M[0][1]=-z*s+(1.0-c)*x*y;
  M[0][2]= y*s+(1.0-c)*x*z;

  M[1][0]= z*s+(1.0-c)*x*y;
  M[1][2]=-x*s+(1.0-c)*y*z;

  M[2][0]=-y*s+(1.0-c)*x*z;
  M[2][1]= x*s+(1.0-c)*y*z;
}


Mat3D::Mat3D(vector<double> m) {
  for (unsigned int i=3; i--; ) {
    for (unsigned int j=3; j--; ) 
      M[i][j]=m[3*j+i];
  }
}


Vec3D Mat3D::operator*(const Vec3D& v) const {
  Vec3D r;
  for (unsigned int i=3; i--; ) {
    double tmp=0.0;
    for (unsigned int j=3; j--; ) 
      tmp += M[i][j]*v[j];
    r[i]=tmp;
  }
  return r;
}

Mat3D Mat3D::operator+(const Mat3D& m) const {
  Mat3D r;
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      r.M[i][j]=M[i][j]+m.M[i][j];
  return r;
}

Mat3D Mat3D::operator-(const Mat3D& m) const {
  Mat3D r;
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      r.M[i][j]=M[i][j]-m.M[i][j];
  return r;
}

Mat3D Mat3D::operator*(const Mat3D& m) const {
  Mat3D r;
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) {
      double tmp=0.0;
      for (unsigned int k=3; k--; ) 
	tmp+=M[i][k]*m.M[k][j];
      r.M[i][j]=tmp;
    }
  return r;
}


Mat3D Mat3D::operator*(double a) const {
  Mat3D r(this);
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      r.M[i][j]*=a;
  return r;
}


Mat3D Mat3D::operator*=(const Mat3D& m) {
  Mat3D r(this);
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) {
      double tmp=0.0;
      for (unsigned int k=3; k--; ) 
	tmp+=r.M[i][k]*m.M[k][j];
      M[i][j]=tmp;
    }
  return *this;
}

Mat3D Mat3D::lmult(const Mat3D& m) {
  Mat3D r(this);
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) {
      double tmp=0.0;
      for (unsigned int k=3; k--; ) 
	tmp+=m.M[i][k]*r.M[k][j];
      M[i][j]=tmp;
    }
  return *this;
}

Mat3D Mat3D::operator*=(double a) {
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      M[i][j]*=a;
  return Mat3D(this);
}


Vec3D Mat3D::operator[](unsigned int i) const {
  if (i<3) 
    return Vec3D(M[i]);
  return Vec3D();
}


double* Mat3D::at(unsigned int i, unsigned int j) {
  if ((i<3) && (j<3)) 
    return &M[i][j];
  //return 0.0;
}



Mat3D Mat3D::orthogonalize() const {
  Mat3D C=(Mat3D()*3.0-((*this)*transpose()))*0.5;
  return C*(*this);
}


Mat3D Mat3D::transpose() const {
  Mat3D r;
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      r.M[j][i]=M[i][j];
  return r;
}

Mat3D Mat3D::inverse() const {
  Mat3D r;
  double d=this->det();
  if (d!=0.0) {
    d=1.0/d;
    r.M[0][0]=d*(M[1][1]*M[2][2]-M[1][2]*M[2][1]);
    r.M[0][1]=d*(M[2][1]*M[0][2]-M[2][2]*M[0][1]);
    r.M[0][2]=d*(M[0][1]*M[1][2]-M[0][2]*M[1][1]);
    r.M[1][0]=d*(M[1][2]*M[2][0]-M[1][0]*M[2][2]);
    r.M[1][1]=d*(M[2][2]*M[0][0]-M[2][0]*M[0][2]);
    r.M[1][2]=d*(M[0][2]*M[1][0]-M[0][0]*M[1][2]);
    r.M[2][0]=d*(M[1][0]*M[2][1]-M[1][1]*M[2][0]);
    r.M[2][1]=d*(M[2][0]*M[0][1]-M[2][1]*M[0][0]);
    r.M[2][2]=d*(M[0][0]*M[1][1]-M[0][1]*M[1][0]);
  }
  return r;
}


double Mat3D::sqSum() const {
  double s=0.0;
  for (unsigned int i=3; i--; ) 
    for (unsigned int j=3; j--; ) 
      s+=M[i][j]*M[i][j];
  return s;
}

double Mat3D::det() const {
  double d=0.0;
  d+=M[0][0]*M[1][1]*M[2][2];
  d+=M[1][0]*M[2][1]*M[0][2];
  d+=M[2][0]*M[0][1]*M[1][2];
  d-=M[0][0]*M[1][2]*M[2][1];
  d-=M[1][0]*M[2][2]*M[0][1];
  d-=M[2][0]*M[0][2]*M[1][1];
  return d;
}

Mat3D Mat3D::QR() {
    Mat3D Q;
    for (unsigned int n=0; n<2; n++) {
        Vec3D u;
        for (unsigned int i=3-n; i--; ) u[2-i]=M[2-i][n];
        u[n]+=u.norm();
        u.normalize();
        Mat3D Qt(u.outer());
        Qt*=2.0;
        for (unsigned int i=3; i--; ) Qt.M[i][i]-=1.0;
        lmult(Qt);
        Q*=Qt;
    }
    return Q;
}

Mat3D Mat3D::QL() {
    Mat3D Q;
    for (unsigned int n=0; n<2; n++) {
        Vec3D u;
        for (unsigned int i=3-n; i--; ) u[i]=M[i][2-n];
        u[2-n]+=u.norm();
        u.normalize();
        Mat3D Qt(u.outer());
        Qt*=2.0;
        for (unsigned int i=3; i--; ) Qt.M[i][i]-=1.0;
        lmult(Qt);
        Q*=Qt;
    }
    return Q;
}

void Mat3D::upperBidiagonal(Mat3D& L, Mat3D& R) {
    for (unsigned int n=0; n<2; n++) {
        Vec3D u;
        for (unsigned int i=3-n; i--; ) u[2-i]=M[2-i][n];
        u[n]+=u.norm();
        u.normalize();
        Mat3D T(u.outer());
        T*=2.0;
        for (unsigned int i=3; i--; ) T.M[i][i]-=1.0;
        lmult(T);
        L*=T;
        
        if (n<1) {
            for (unsigned int i=3; i--; ) u[i]=(i<=n)?0.0:M[n][i];
            u[n+1]+=u.norm();
            u.normalize();
            T=u.outer();
            T*=2.0;
            for (unsigned int i=3; i--; ) T.M[i][i]-=1.0;
            (*this)*=T;
            R.lmult(T);
        }
    }
}
