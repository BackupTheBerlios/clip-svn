#ifndef __DIFFRACT_H__
#define __DIFFRACT_H__

//#include <cctbx/crystal/symmetry.h>

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

  enum ProjectionType {Plane, Cylinder};

  Diffract();
  ~Diffract();

  bool setSym(string s, vector<double>);

  bool setReflexConditions(vector<ReflexCondition>);

  void generateReflex();
  void generateScatteredRayDirections();
  
  void setProjection(Diffract::ProjectionType type, Mat3D localCoord, Vec3D v);
  void calcProjection ();

  // projects a vector of the reziprocal space to the corresponding reflection spot on the detector surface
  vector<double> rSpace2Det(Vec3D v);
  // projects an point of the detector surface to the corresponding reflex in reziprocal space 
  Vec3D det2RSpace(vector<double> p);

  void addRotation(Vec3D angle, double angle);
  void setRotation(Mat3D M);

  unsigned int reflexCount();
  Reflex getReflex(unsigned int i);

  unsigned int scatteringReflexCount();
  Reflex getScatteringReflex(unsigned int i);

  unsigned int projectedReflexCount();
  Reflex getProjectedReflex(unsigned int i);
  vector<double> getProjectedCoord(unsigned int i);

  vector<vector<double> > getCoord();


  Vec3D reduced2Real(Vec3D);
  Vec3D reduced2Rezi(Vec3D);

  vector<double> boxSize;

  Mat3D getRealOrientationMatrix();
  Mat3D getReziprocalOrientationMatrix();
  Mat3D getRotationMatrix();


 private:
  Mat3D M_real;
  Mat3D M_rezi;
  Mat3D rot;

  ProjectionType projectionType;
  //M_proj is the local coordinate-system of the detector
  Mat3D M_proj;
  // on PlaneProjection, V_proj.x and .y are the displacements of the detector-Zeropoint
  // V_proj.z is the sample-detector distance 
  Vec3D V_proj;

  vector<Reflex> reflexe;
  vector<unsigned int> scatteringRef;
  vector<unsigned int> projectedRef;
  vector<vector<double> > projectedCoords;
  //cctbx::sgtbx::space_group* sg;
  vector<double> cell;
  vector<ReflexCondition> reflexCond;
};


#endif
