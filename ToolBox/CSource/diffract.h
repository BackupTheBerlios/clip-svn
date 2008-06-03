#ifndef __DIFFRACT_H__
#define __DIFFRACT_H__

#include <vector>
#include <string>

#include "mat3D.h"


using namespace std;


int ggt(int a, int b);


struct Reflex {
  int h;
  int k;
  int l;
  
  double d;
  vector<int> orders;
  
  int lowestDiffOrder;

  Vec3D normal;
  Vec3D scatteredRay;
  
  double projX;
  double projY;
  
};

class ReflexCondition {
  public:
    ReflexCondition() {};
    ReflexCondition(int _h, int _k, int _l, int _m, bool hz, bool kz, bool lz) {
        h=_h;
        k=_k;
        l=_l;
        modulo=_m;
        hZero=hz;
        kZero=kz;
        lZero=lz;
    }
    ~ReflexCondition() {};

    int h;
    int k;
    int l;
    int modulo;
    bool hZero;
    bool kZero;
    bool lZero;
};

class Diffract {
 public:

  Diffract();
  ~Diffract();

  bool setCell(vector<double>);

  bool setReflexConditions(vector<ReflexCondition>);

  void generateReflections();
  void generateScatteredRayDirections();
  
  void addRotation(Vec3D angle, double angle);
  void setRotation(Mat3D M);

  unsigned int reflectionCount();
  Reflex getReflex(unsigned int i);

  unsigned int scatteredReflectionCount();
  Reflex getScatteredReflex(unsigned int i);

  Vec3D reduced2Real(Vec3D);
  Vec3D reduced2Rezi(Vec3D);

  Mat3D getRealOrientationMatrix();
  Mat3D getReziprocalOrientationMatrix();
  Mat3D getRotationMatrix();


 private:
  Mat3D Mreal;
  Mat3D Mrezi;
  Mat3D rot;

  vector<Reflex> reflexe;
  vector<unsigned int> scatteredIdx;
  vector<double> cell;
  vector<ReflexCondition> reflexCond;
};


#endif
