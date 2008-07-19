

class Mat3D {

%TypeHeaderCode
#include <mat3D.h>
#include <iostream>
%End

 
 public:
  Mat3D();
  Mat3D(Vec3D v1, Vec3D v2,  Vec3D v3);
  Mat3D(Vec3D axis, double angle);
  Mat3D(const Mat3D* t);

  Mat3D(SIP_PYOBJECT _x);
%MethodCode
  PyObject* iter=PyObject_GetIter(a0);
  if (iter==NULL) {
    sipIsErr=1;
  } else {
    vector<double> m;
    unsigned int itercount=0;
    PyObject* coliter;
    double t;
    for (PyObject* item=PyIter_Next(iter); item && itercount<9; item=PyIter_Next(iter)) {
      if (PyFloat_Check(item) || PyInt_Check(item)) {
        PyArg_Parse(item, "d", &t);
  	//std::cout << "parsed Float " << t << std::endl;
     	m.push_back(t);
        itercount++;
      } else {
        try {
          coliter=PyObject_GetIter(item);
        }
        catch (...) {
          coliter=NULL;
        }
        if (coliter!=NULL) {
        
          //std::cout << "parsed iter" << std::endl;
          for (PyObject* colitem=PyIter_Next(coliter); colitem && itercount<9; colitem=PyIter_Next(coliter)) {
            //std::cout << "colIter loop" << std::endl;
            if (PyFloat_Check(colitem) || PyInt_Check(colitem)) {
              PyArg_Parse(colitem, "d", &t);
              //std::cout << "parsed float in iter" << t << std::endl;
              m.push_back(t);
            }
            itercount++;
	  }
        } else {
          itercount++;
        }
      }
    }
    if (m.size()==9) {
      Py_BEGIN_ALLOW_THREADS
      sipCpp = new Mat3D(m);
      Py_END_ALLOW_THREADS
    } else {
      sipIsErr=1;
    }
  }
%End  


  
  Vec3D operator*(const Vec3D& v) const;
  Mat3D operator*(const Mat3D& m) const;
  Mat3D operator*(double a) const;

  Mat3D operator-(const Mat3D& m) const;
  Mat3D operator+(const Mat3D& m) const;
  Mat3D lmult(const Mat3D& m);
  // SIP Bug :-(
  //Mat3D operator*=(const Mat3D& m) /Numeric/;
  //Mat3D operator*=(double a) /Numeric/;
  
  Mat3D orthogonalize() const;
  Mat3D transposed() const;
  void transpose();
  Mat3D inverse() const;
  double sqSum() const;
  double det() const;
  
  Mat3D QR();
  Mat3D QL();
  void upperBidiagonal(Mat3D& L /Out/, Mat3D& R /Out/);
  void svd(Mat3D& L /Out/, Mat3D& R /Out/);
  
  
  SIP_PYOBJECT __getitem__(SIP_PYOBJECT _x);
%MethodCode
    int idx1;
    PyObject* iter;
    if (PyInt_Check(a0) && PyArg_Parse(a0, "i", &idx1)) {
        Vec3D *v;
        Py_BEGIN_ALLOW_THREADS
        v=new Vec3D((*sipCpp)[idx1]);
        Py_END_ALLOW_THREADS
        sipRes=sipConvertFromNewInstance(v,sipClass_Vec3D,NULL);
        sipIsErr=0;
    } else if ((iter=PyObject_GetIter(a0))) {
        int idx2;
        PyObject* item;
        if ((item=PyIter_Next(iter)) && PyInt_Check(item) && PyArg_Parse(item, "i", &idx1) && (item=PyIter_Next(iter)) && PyInt_Check(item) && PyArg_Parse(item, "i", &idx2)) {
            double d;
            Py_BEGIN_ALLOW_THREADS
            d = *((*sipCpp).at(idx1,idx2));
            Py_END_ALLOW_THREADS
            sipRes=PyFloat_FromDouble(d);
        } else {
          sipIsErr=1;
        }
    } else {
      sipIsErr=1;
    }
%End
  
  void __setitem__(int i, int j, double d);
%MethodCode
    Py_BEGIN_ALLOW_THREADS
    *(*sipCpp).at(a0,a1)=a2;
    Py_END_ALLOW_THREADS
%End



  SIP_PYOBJECT __repr__();
%MethodCode
  char c[256];
  sprintf (c, "[[%f %f %f]\n[%f %f %f]\n[%f %f %f]]", (*sipCpp)[0][0], (*sipCpp)[0][1], (*sipCpp)[0][2], (*sipCpp)[1][0], (*sipCpp)[1][1], (*sipCpp)[1][2], (*sipCpp)[2][0], (*sipCpp)[2][1], (*sipCpp)[2][2]);
  sipRes=PyString_FromString(c);
%End



};


