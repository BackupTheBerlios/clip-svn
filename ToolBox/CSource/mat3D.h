#ifndef __MAT3D_H__
#define __MAT3D_H__

#include "vec3D.h"
#include <vector>

using namespace std;


class Mat3D {
 public:
  Mat3D();
  Mat3D(Vec3D v1, Vec3D v2,  Vec3D v3);
  Mat3D(vector<double> m);
  Mat3D(Vec3D axis, double angle);
  Mat3D(const Mat3D* t);
  
  Vec3D operator*(const Vec3D& v) const;
  Mat3D operator*(const Mat3D& m) const;
  Mat3D operator*(double a) const;

  Mat3D operator-(const Mat3D& m) const;
  Mat3D operator+(const Mat3D& m) const;

  Mat3D operator*=(const Mat3D& m);
  Mat3D operator*=(double a);

  Vec3D operator[](unsigned int i) const;
  double* at(unsigned int i, unsigned int j);
  
  Mat3D orthogonalize() const;
  Mat3D transpose() const;
  Mat3D inverse() const;
  double sqSum() const;
  double det() const;
  

 private:
  double M[3][3];
};


//Mat3D operator*(double a, const Mat3D& m);

#endif
