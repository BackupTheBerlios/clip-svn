#ifndef __VEC3D__
#define __VEC3D__

class Vec3D {
  public:
    Vec3D();
    Vec3D(double x, double y, double z);
    Vec3D(const double _x[3]);
    Vec3D(const Vec3D* v);

    Vec3D operator+(const Vec3D& v);
    Vec3D operator-(const Vec3D& v);
    Vec3D operator*(double a);
    double operator*(const Vec3D& v);
    Vec3D operator%(const Vec3D &v);
    Vec3D operator/(double a);

    bool operator==(const Vec3D& v);
    bool operator!=(const Vec3D& v);
    bool isNull();

    Vec3D operator+=(const Vec3D& v);
    Vec3D operator-=(const Vec3D& v);
    Vec3D operator*=(double a);
    Vec3D operator/=(double a);

    double& operator[](unsigned int i);
    double operator[](unsigned int i) const;
    
    double norm();
    double norm_sq();
    void normalize();
    Vec3D normalized() const;

    char* __repr__();
    //bool __eq__(Vec3D &v);
    
    double x();
    double y();
    double z();

  private:
    double X[3]; 
};

#endif
