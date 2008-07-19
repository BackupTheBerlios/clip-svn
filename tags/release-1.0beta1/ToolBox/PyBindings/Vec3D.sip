
class Vec3D { 
  
%TypeHeaderCode
#include <vec3D.h>
%End

public:
  Vec3D();
  Vec3D(double x, double y, double z);
  Vec3D(Vec3D* v);

  Vec3D(SIP_PYTUPLE _x);
%MethodCode
  double x,y,z;
  if (PyArg_ParseTuple(a0,"ddd",&x, &y, &z)) {
    Py_BEGIN_ALLOW_THREADS
    sipCpp = new Vec3D(x,y,z);
    Py_END_ALLOW_THREADS
  }
%End  

  Vec3D(SIP_PYLIST _x);
%MethodCode
  double v[3];
  if (PyList_GET_SIZE(a0)<3) {
    sipIsErr=1;
  } else {
    unsigned int good=0;
    for (int i=0; i<3; i++) {
        double t;
	if (PyArg_Parse(PyList_GET_ITEM(a0, i), "d", &t)) {
          v[i]=t;
          good++;
        }
    }
    if (good==3) {
      Py_BEGIN_ALLOW_THREADS
      sipCpp = new Vec3D(v);
      Py_END_ALLOW_THREADS
    } else {
      sipIsErr=1;
    }
  }
%End  

  

  Vec3D operator+(const Vec3D& v);
  Vec3D operator-(const Vec3D& v);
  Vec3D operator*(double a);
  double operator*(const Vec3D& v);
  Vec3D operator%(const Vec3D &v);
  Mat3D operator^(const Vec3D &v);
  Vec3D operator/(double a);

  bool operator==(const Vec3D& v);
  bool operator!=(const Vec3D& v);
  bool isNull();


  // SIP Bug :-(
  //Vec3D operator+=(const Vec3D& v);
  //Vec3D operator-=(const Vec3D& v);
  //Vec3D operator*=(double a);
  //Vec3D operator/=(double a);

  Mat3D outer();
  double norm();
  double norm_sq();
  void normalize();
  Vec3D normalized() const;
  
  double __getitem__(int i);
%MethodCode
    if (a0<3) {
    Py_BEGIN_ALLOW_THREADS
        sipRes = (*sipCpp)[a0];
    Py_END_ALLOW_THREADS
    } else {
        PyErr_SetString(PyExc_IndexError, "3d vectors only have 3 components");
        sipIsErr=1;
        sipRes=0.0;
    }
%End
 
  void __setitem__(int i, double d);
%MethodCode
    if (a0<3) {
    Py_BEGIN_ALLOW_THREADS
        (*sipCpp)[a0]=a1;
    Py_END_ALLOW_THREADS
    } else {
        // Raise IndexError
        PyErr_SetString(PyExc_IndexError, "3d vectors only have 3 items");
        sipIsErr=1;
    }
%End
  //bool __eq__(Vec3D &v);

  int __len__();
%MethodCode
    Py_BEGIN_ALLOW_THREADS
    sipRes=3;
    Py_END_ALLOW_THREADS
%End

  
  double x();
  double y();
  double z();

  SIP_PYOBJECT __repr__();
%MethodCode
  char c[128];
  sprintf (c, "[%f %f %f]", (*sipCpp)[0], (*sipCpp)[1], (*sipCpp)[2]);
  sipRes=PyString_FromString(c);
%End

};

