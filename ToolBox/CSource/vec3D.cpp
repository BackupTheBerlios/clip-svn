#include "vec3D.h"
#include <cmath>
#include <stdio.h>


using namespace std;

Vec3D::Vec3D(){
  for (unsigned int i=3; i--; ) X[i] = 0.0;
}

Vec3D::Vec3D(double _x, double _y, double _z) {
  X[0]=_x;
  X[1]=_y;
  X[2]=_z;
}

Vec3D::Vec3D(const double _x[3]) {
  for (unsigned int i=3; i--; ) X[i] = _x[i];
}

Vec3D::Vec3D(const Vec3D* v) {
  for (unsigned int i=3; i--; ) X[i] = v->X[i];
}

Vec3D Vec3D::operator+(const Vec3D& v){
  Vec3D r(this);
  for (unsigned int i=3; i--; ) r.X[i] += v.X[i];
  return r;
}

Vec3D Vec3D::operator-(const Vec3D& v){
  Vec3D r(this);
  for (unsigned int i=3; i--; ) r.X[i] -= v.X[i];
  return r;
}

double Vec3D::operator*(const Vec3D& v){
  double p=0.0;
  for (unsigned int i=3; i--; ) p+=X[i]*v.X[i];
  return p;
}

Vec3D Vec3D::operator*(double a){
  Vec3D r(this);
  for (unsigned int i=3; i--; ) r.X[i] *= a;
  return r;
}

Vec3D Vec3D::operator%(const Vec3D &v){
  Vec3D r;
  r.X[0]=X[1]*v.X[2]-X[2]*v.X[1];
  r.X[1]=X[2]*v.X[0]-X[0]*v.X[2];
  r.X[2]=X[0]*v.X[1]-X[1]*v.X[0];
  return r;
}

Vec3D Vec3D::operator/(double a) {
  if (a==0) return Vec3D(this);
  Vec3D r(this);
  for (unsigned int i=3; i--; ) r.X[i] /= a;
  return r;
}


Vec3D Vec3D::operator+=(const Vec3D& v){
  for (unsigned int i=3; i--; ) X[i] += v.X[i];
  return Vec3D(this);
}

Vec3D Vec3D::operator-=(const Vec3D& v){
  for (unsigned int i=3; i--; ) X[i] -= v.X[i];
  return Vec3D(this);
}

Vec3D Vec3D::operator*=(double a){
  for (unsigned int i=3; i--; ) X[i] *= a;
  return Vec3D(this);
}

Vec3D Vec3D::operator/=(double a) {
  if (a!=0)
    for (unsigned int i=3; i--; ) X[i] /= a;
  return Vec3D(this);
}

double Vec3D::norm() {
  return sqrt(X[0]*X[0]+X[1]*X[1]+X[2]*X[2]);
}

double Vec3D::norm_sq() {
  return X[0]*X[0]+X[1]*X[1]+X[2]*X[2];
}

void Vec3D::normalize() {
  double n=norm();
  if (n!=0) 
    for (unsigned int i=3; i--; ) X[i] /= n;
}

Vec3D Vec3D::normalized() const {
  Vec3D v=Vec3D(this);
  v.normalize();
  return v;
}

double Vec3D::x() {
  return X[0];
}

double Vec3D::y() {
  return X[1];
}

double Vec3D::z() {
  return X[2];
}

double& Vec3D::operator[](unsigned int i) {
  static double err=0.0;
  if (i<3)
    return X[i];
  return err;
}

double Vec3D::operator[](unsigned int i) const {
  if (i<3)
    return X[i];
  return 0.0;
}


bool Vec3D::operator==(const Vec3D& v) {
  return (X[0]==v.X[0]) && (X[1]==v.X[1]) && (X[2]==v.X[2]);
}

bool Vec3D::operator!=(const Vec3D& v) {
  return (X[0]!=v.X[0]) || (X[1]!=v.X[1]) || (X[2]!=v.X[2]);
}

bool Vec3D::isNull() {
  return (X[0]==0.0) && (X[1]==0.0) && (X[2]==0.0);
}



  char* Vec3D::__repr__() {
  char c[1024];
  sprintf (c, "[%f %f %f]", X[0], X[1], X[2]);
  return c;
  }
/*

  double Vec3D::__getitem__(int i) {
  return X[i];
  }

  void Vec3D::__setitem__(int i, double d) {
  X[i]=d;
  }
  
  bool Vec3D::__eq__(Vec3D &v) {
  for (unsigned int i=0; i<3; i++)
  if (X[i]!=v.X[i])
  return false;
  return true;
  }
*/
